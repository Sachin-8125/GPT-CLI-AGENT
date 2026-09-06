from __future__ import annotations

import uuid

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .nodes import generate_command_node, route_after_safety, screen_command_node, execute_command_node, blocked_node
from .state import AgentState

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("generate_command", generate_command_node)
    workflow.add_node("screen_command", screen_command_node)
    workflow.add_node("execute_command", execute_command_node)
    workflow.add_node("blocked", blocked_node)
    
    workflow.set_entry_point("generate_command")
    workflow.add_edge("generate_command", "screen_command")
    workflow.add_conditional_edges(
        "screen_command",
        route_after_safety,
        {
            "execute_command": "execute_command",
            "blocked": "blocked"
        }
    )
    workflow.add_edge("execute_command", END)
    workflow.add_edge("blocked", END)

    return workflow.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["execute_command"],
    )


def thread_config():
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


def run_agent(prompt: str, auto: bool = True) -> AgentState:
    graph = build_graph()
    config = thread_config()
    graph.invoke({"prompt": prompt}, config=config)
   

    if auto:
        graph.invoke(None, config)

    return graph.get_state(config).values
