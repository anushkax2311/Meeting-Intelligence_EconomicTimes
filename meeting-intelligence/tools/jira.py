import os
import httpx


def create_jira_ticket(inp: dict) -> str:
    base_url    = os.getenv("JIRA_BASE_URL")
    email       = os.getenv("JIRA_EMAIL")
    token       = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY", "MI")

    # No credentials → return a mock URL for demo
    if not all([base_url, email, token]):
        slug = inp["summary"].lower().replace(" ", "-")[:20]
        return f"https://demo.atlassian.net/browse/{project_key}-MOCK-{slug}"

    payload = {
        "fields": {
            "project":   {"key": project_key},
            "summary":   inp["summary"],
            "issuetype": {"name": "Task"},
            "priority":  {"name": inp.get("priority", "Medium")},
        }
    }
    if inp.get("due_date"):
        payload["fields"]["duedate"] = inp["due_date"]

    response = httpx.post(
        f"{base_url}/rest/api/3/issue",
        json=payload,
        auth=(email, token),
        headers={"Accept": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    key = response.json()["key"]
    return f"{base_url}/browse/{key}"