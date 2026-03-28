from typing import TypedDict, Annotated, List
import operator


class Task(TypedDict):
    description: str
    owner: str        # "" if unknown
    deadline: str     # "" if none stated
    priority: str     # high | medium | low
    confidence: str   # high | low
    jira_url: str     # filled by action_node


class Gap(TypedDict):
    task_description: str
    issue: str
    suggestion: str


class AuditEntry(TypedDict):
    stage: str
    event: str
    reasoning: str
    ts: str


class WorkflowState(TypedDict):
    transcript:   str
    tasks:        List[Task]
    decisions:    List[str]
    ambiguities:  List[str]
    gaps:         List[Gap]
    retry_count:  int
    stage:        str
    error:        str
    audit_trail:  Annotated[List[AuditEntry], operator.add]  # append-only