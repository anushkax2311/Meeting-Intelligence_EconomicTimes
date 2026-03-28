import asyncio
import os
from datetime import datetime, timezone

from api.db import get_stale_tasks, update_escalation, append_audit
from tools.slack import send_slack_message

STALE_AFTER_HOURS   = int(os.getenv("STALE_AFTER_HOURS",   "48"))
CHECK_INTERVAL_MINS = int(os.getenv("CHECK_INTERVAL_MINS",  "30"))


async def staleness_monitor():
    print(f"[Monitor] Started. Checking every {CHECK_INTERVAL_MINS}min "
          f"for tasks stale >{STALE_AFTER_HOURS}h.")
    while True:
        await asyncio.sleep(CHECK_INTERVAL_MINS * 60)
        try:
            await check_and_escalate()
        except Exception as e:
            print(f"[Monitor] Error: {e}")


async def check_and_escalate():
    stale = get_stale_tasks(STALE_AFTER_HOURS)
    if not stale:
        return
    print(f"[Monitor] {len(stale)} stale task(s) found.")
    for task in stale:
        await escalate(task)


async def escalate(task: dict):
    level     = task["escalation_level"]
    hours     = _hours_since(task["last_updated_at"])
    new_level = min(level + 1, 3)
    target    = _target(level, task)

    send_slack_message({"user": target, "message": _message(level, task, hours)})
    update_escalation(task["id"], new_level)
    append_audit(task["thread_id"], {
        "stage":     "monitor",
        "event":     "ESCALATED",
        "reasoning": f"Task stale {hours:.0f}h. Level {level}→{new_level}. Notified: {target}",
        "ts":        datetime.now(timezone.utc).isoformat()
    })


def _target(level: int, task: dict) -> str:
    if level == 0: return task["owner"] or "team"
    if level == 1: return f"{task['owner']}'s manager"
    return "ops-team"


def _message(level: int, task: dict, hours: float) -> str:
    desc     = task["description"]
    owner    = task["owner"] or "Unassigned"
    deadline = task["deadline"] or "No deadline set"
    if level == 0:
        return (f"*Reminder* — your task has been open for *{hours:.0f} hours*.\n"
                f"> {desc}\nDeadline: {deadline}")
    if level == 1:
        return (f"*Escalation* — task assigned to *{owner}* stale for *{hours:.0f}h*.\n"
                f"> {desc}\nDeadline: {deadline}")
    return (f"*OPS ALERT* — unresolved after *{hours:.0f}h*. Manual intervention needed.\n"
            f"> {desc}\nOwner: {owner} | Deadline: {deadline}")


def _hours_since(ts: str) -> float:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except Exception:
        return 0.0