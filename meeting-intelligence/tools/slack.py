import os
import httpx


def send_slack_message(inp: dict) -> None:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    payload = {
        "blocks": [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Meeting Intelligence* — Hi *{inp['user']}*\n{inp['message']}"
            }
        }]
    }

    if not webhook_url:
        print(f"[SLACK MOCK] To: {inp['user']}\n{inp['message']}\n")
        return

    response = httpx.post(webhook_url, json=payload, timeout=5)
    response.raise_for_status()  