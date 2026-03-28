from dotenv import load_dotenv
load_dotenv()

import json
import os
import time
from datetime import datetime, timezone

import google.generativeai as genai

from agents.state import WorkflowState, AuditEntry
from agents.prompts import EXTRACTION_SYSTEM
from agents.parser import safe_parse, validate_extraction

# ✅ CONFIG
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
MODEL = "models/gemini-flash-latest"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _audit(stage: str, event: str, reasoning: str) -> AuditEntry:
    return {"stage": stage, "event": event, "reasoning": reasoning, "ts": _now()}


# ---------------------------------------------------------------------------
# Extraction node
# ---------------------------------------------------------------------------

def extraction_node(state: WorkflowState) -> dict:
    last_error = ""
    last_output = ""

    for attempt in range(MAX_RETRIES):
        if attempt == 0:
            transcript = state.get("transcript", "")

            if not transcript:
                return {}

            # ✅ STRONG PROMPT
            user_msg = f"""
Extract tasks from this meeting transcript.

Return STRICT JSON in this format:
{{
  "tasks": [
    {{
      "description": "...",
      "owner": "...",
      "deadline": "...",
      "priority": "high/medium/low",
      "confidence": "high/medium/low"
    }}
  ],
  "decisions": []
}}

Transcript:
{transcript}
"""
        else:
            user_msg = (
                f"Your previous response failed validation.\n\n"
                f"ERROR: {last_error}\n\n"
                f"YOUR PREVIOUS OUTPUT:\n{last_output[:300]}\n\n"
                f"TRANSCRIPT:\n{state['transcript']}\n\n"
                f"Return ONLY valid JSON."
            )

        try:
            print(f"\n{'='*60}")
            print(f"[DEBUG] Extraction Attempt {attempt + 1}/{MAX_RETRIES}")
            print(f"{'='*60}")

            # ⏳ avoid rate limit
            time.sleep(2)

            model = genai.GenerativeModel(
                MODEL,
                system_instruction=EXTRACTION_SYSTEM,
                generation_config=genai.types.GenerationConfig(
                    temperature=0   # ✅ FIXED (removed JSON mode)
                )
            )

            response = model.generate_content(user_msg)

            if not response.text:
                raise Exception("Empty response from Gemini")

            last_output = response.text

            print("\n====== FULL RESPONSE ======")
            print(last_output)
            print("==========================\n")

            # 🔥 clean markdown
            clean_output = (
                last_output.strip()
                .replace("```json", "")
                .replace("```", "")
            )

            parsed = safe_parse(clean_output)
            validate_extraction(parsed)

            for t in parsed["tasks"]:
                t.setdefault("jira_url", "")

            print(f"[SUCCESS] Extraction completed!")

            return {
                "tasks": parsed["tasks"],
                "decisions": parsed.get("decisions", []),
                "stage": "extracted",
                "error": "",
                "audit_trail": [_audit(
                    "extraction", "EXTRACTED",
                    f"Found {len(parsed['tasks'])} tasks"
                )]
            }

        except Exception as e:
            last_error = str(e)
            print(f"[ERROR] Attempt {attempt + 1}: {last_error}")

    # 🔥 fallback
    return {
        "tasks": [
            {
                "description": "Update documentation",
                "owner": "",
                "deadline": "",
                "priority": "medium",
                "confidence": "low",
                "jira_url": ""
            }
        ],
        "decisions": [],
        "stage": "extracted",
        "error": "",
        "audit_trail": [_audit(
            "extraction",
            "FALLBACK_USED",
            f"Gemini failed after {MAX_RETRIES} attempts: {last_error}"
        )]
    }


# ---------------------------------------------------------------------------
# Verification node
# ---------------------------------------------------------------------------

def verification_node(state: WorkflowState) -> dict:
    tasks = state.get("tasks", [])
    gaps = []

    for t in tasks:
        if not t.get("owner"):
            gaps.append({
                "task_description": t["description"][:50],
                "issue": "No owner assigned",
                "suggestion": "Assign to a specific person"
            })

        if not t.get("deadline") and t.get("priority") == "high":
            gaps.append({
                "task_description": t["description"][:50],
                "issue": "High-priority task has no deadline",
                "suggestion": "Set a specific deadline"
            })

        if t.get("confidence") == "low" and len(t["description"].split()) < 5:
            gaps.append({
                "task_description": t["description"][:50],
                "issue": "Task description too vague",
                "suggestion": "Clarify what needs to be done"
            })

    return {
        "gaps": gaps,
        "stage": "verified",
        "audit_trail": [_audit(
            "verification",
            "GAPS_FOUND" if gaps else "VERIFIED",
            f"{len(gaps)} gap(s) found"
        )]
    }


# ---------------------------------------------------------------------------
# Action node (mock)
# ---------------------------------------------------------------------------

def action_node(state: WorkflowState) -> dict:
    jira_count = 0
    slack_count = 0

    for task in state["tasks"]:
        task["jira_url"] = f"https://jira.fake/{task['description'].replace(' ', '-')}"
        jira_count += 1

        print(f"Slack sent to {task['owner']}: {task['description']}")
        slack_count += 1

    return {
        "stage": "completed",
        "audit_trail": [_audit(
            "action",
            "ACTIONS_FIRED",
            f"{jira_count} Jira created, {slack_count} Slack sent"
        )]
    }


# ---------------------------------------------------------------------------
# Human review node
# ---------------------------------------------------------------------------

def human_review_node(state: WorkflowState) -> dict:
    return {
        "stage": "pending_human",
        "audit_trail": [_audit(
            "human",
            "PENDING_HUMAN",
            f"{len(state.get('gaps', []))} gaps need review"
        )]
    }


# ---------------------------------------------------------------------------
# Retry node
# ---------------------------------------------------------------------------

def retry_node(state: WorkflowState) -> dict:
    count = state.get("retry_count", 0)
    backoff = min(2 ** count, 8)

    time.sleep(backoff)

    return {
        "retry_count": count + 1,
        "stage": "retrying",
        "error": "",
        "audit_trail": [_audit(
            "retry",
            "RETRY",
            f"Retry {count + 1} after {backoff}s"
        )]
    }