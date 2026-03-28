from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver  # ✅ correct import

from agents.state import WorkflowState
from agents.nodes import (
    extraction_node,
    verification_node,
    action_node,
    human_review_node,
    retry_node,
)

MAX_RETRIES = 3


def route_after_extraction(state: WorkflowState) -> str:
    if state.get("error"):
        if state.get("retry_count", 0) >= MAX_RETRIES:
            return END
        return "retry_node"
    return "verification_node"


def route_after_verification(state: WorkflowState) -> str:
    if state.get("gaps"):
        return "human_review_node"
    return "action_node"


def build_graph():
    builder = StateGraph(WorkflowState)

    # Add nodes
    builder.add_node("extraction_node", extraction_node)
    builder.add_node("verification_node", verification_node)
    builder.add_node("action_node", action_node)
    builder.add_node("human_review_node", human_review_node)
    builder.add_node("retry_node", retry_node)

    # Flow
    builder.add_edge(START, "extraction_node")
    builder.add_conditional_edges("extraction_node", route_after_extraction)
    builder.add_conditional_edges("verification_node", route_after_verification)
    builder.add_edge("retry_node", "extraction_node")
    builder.add_edge("human_review_node", "action_node")
    builder.add_edge("action_node", END)

    # ✅ Use MemorySaver (no sqlite needed)
    checkpointer = MemorySaver()

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review_node"],
    )


graph = build_graph()