import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

load_dotenv()

from agents.graph import graph
from api.db import init_db, save_tasks, append_audit, get_audit, mark_task_complete
from api.monitor import staleness_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    monitor_task = asyncio.create_task(staleness_monitor())
    yield
    monitor_task.cancel()


app = FastAPI(title="Meeting Intelligence API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

if os.path.exists("dashboard"):
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


class RunRequest(BaseModel):
    transcript: str

class ApproveRequest(BaseModel):
    approver:    str
    fixed_tasks: list
    notes:       str = ""


@app.post("/run")
async def run_workflow(body: RunRequest):
    thread_id = str(uuid.uuid4())
    config    = {"configurable": {"thread_id": thread_id}}
    initial   = {
        "transcript":  body.transcript,
        "tasks":       [], "decisions": [], "ambiguities": [],
        "gaps":        [], "retry_count": 0,
        "stage":       "received", "error": "",
        "audit_trail": [{
            "stage": "orchestrator", "event": "STARTED",
            "reasoning": "Transcript received, beginning extraction.",
            "ts": datetime.now(timezone.utc).isoformat()
        }]
    }
    result = graph.invoke(initial, config)
    if result.get("tasks"):
        save_tasks(thread_id, result["tasks"])
    for entry in result.get("audit_trail", []):
        append_audit(thread_id, entry)
    return {
        "thread_id": thread_id,
        "stage":     result.get("stage"),
        "tasks":     result.get("tasks", []),
        "decisions": result.get("decisions", []),
        "gaps":      result.get("gaps", []),
    }


@app.post("/approve/{thread_id}")
async def approve_workflow(thread_id: str, body: ApproveRequest):
    config = {"configurable": {"thread_id": thread_id}}
    graph.update_state(config, {
        "gaps":  [],
        "tasks": body.fixed_tasks,
        "audit_trail": [{
            "stage": "human", "event": "APPROVED",
            "reasoning": f"Approved by {body.approver}. Notes: {body.notes or 'none'}",
            "ts": datetime.now(timezone.utc).isoformat()
        }]
    })
    result = graph.invoke(None, config)
    for entry in result.get("audit_trail", []):
        append_audit(thread_id, entry)
    return {"thread_id": thread_id, "stage": result.get("stage"),
            "tasks": result.get("tasks", [])}


@app.get("/audit/{thread_id}")
async def get_audit_trail(thread_id: str):
    return get_audit(thread_id)


@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str):
    mark_task_complete(task_id)
    return {"status": "ok"}


@app.get("/stream/{thread_id}")
async def stream_audit(thread_id: str):
    async def generator():
        seen = 0
        while True:
            rows = get_audit(thread_id)
            for entry in rows[seen:]:
                yield {"data": json.dumps(entry)}
                seen += 1
            await asyncio.sleep(2)
    return EventSourceResponse(generator())


@app.get("/health")
async def health():
    return {"status": "ok"}
