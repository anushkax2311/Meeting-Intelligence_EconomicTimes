import pytest

from agents.parser import safe_parse
from agents.nodes import verification_node


# ---------------- PARSER TEST ---------------- #

def test_safe_parse_valid_json():
    text = '{"tasks": [], "decisions": []}'
    result = safe_parse(text)

    assert isinstance(result, dict)
    assert "tasks" in result
    assert "decisions" in result


def test_safe_parse_with_markdown():
    text = """```json
    {"tasks": [], "decisions": []}
    ```"""
    result = safe_parse(text)

    assert isinstance(result, dict)
    assert "tasks" in result


# ---------------- VERIFICATION TEST ---------------- #

def test_verification_detects_missing_owner():
    state = {
        "tasks": [
            {
                "description": "Update docs",
                "owner": "",
                "deadline": "Friday",
                "priority": "medium"
            }
        ]
    }

    result = verification_node(state)

    assert len(result["gaps"]) > 0
    assert "missing owner" in result["gaps"][0].lower()


def test_verification_no_gaps():
    state = {
        "tasks": [
            {
                "description": "Build API",
                "owner": "John",
                "deadline": "Friday",
                "priority": "high"
            }
        ]
    }

    result = verification_node(state)

    assert result["gaps"] == []