import json
import re


def safe_parse(text: str) -> dict:
    """Parse Claude's response to JSON. Handles all real-world edge cases."""
    text = text.strip()

    # 1. Direct parse — happy path (~95% of calls)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences ```json...``` or ```...```
    fenced = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
    fenced = re.sub(r'\n?```\s*$', '', fenced, flags=re.MULTILINE).strip()
    try:
        return json.loads(fenced)
    except json.JSONDecodeError:
        pass

    # 3. Extract first {...} block (Claude added preamble prose)
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 4. Raise with context so retry node can report it clearly
    preview = text[:200].replace('\n', ' ')
    raise ValueError(f"Could not parse JSON from Claude output: {preview}")


def validate_extraction(data: dict):
    """Raise AssertionError with a clear message if the schema is wrong."""
    assert "tasks" in data,     "Missing 'tasks' key"
    assert "decisions" in data, "Missing 'decisions' key"
    assert isinstance(data["tasks"], list), "'tasks' must be a list"
    for i, t in enumerate(data["tasks"]):
        for field in ["description", "owner", "deadline", "priority", "confidence"]:
            assert field in t, f"Task {i} missing field: '{field}'"
        assert t["priority"] in ["high", "medium", "low"], \
            f"Task {i} invalid priority: '{t['priority']}'"
        assert t["confidence"] in ["high", "low"], \
            f"Task {i} invalid confidence: '{t['confidence']}'"