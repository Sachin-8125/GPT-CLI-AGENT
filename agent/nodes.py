from __future__ import annotations
from .executor import run_command
from .safety import screen_command
from .llm import generate_command
from .state import AgentState


def generate_command_node(state: AgentState) -> AgentState:
    command, explanation = generate_command(state['prompt'])
    return {"command": command, "explanation": explanation}


def screen_command_node(state: AgentState) -> AgentState:
    is_safe, reason = screen_command(state['command'])
    return {"is_safe": is_safe, "safety_reason": reason}


def execute_command_node(state: AgentState) -> AgentState:
    if not state.get("is_safe", True):
        return {
            "executed": False,
            "stdout": "",
            "stderr": "Execution blocked for safety reasons" + state.get("safety_reason", ""),
            "exit_code": None
        }

    result = run_command(state['command'])
    return {
        "executed": True,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code
    }


def blocked_node(state: AgentState) -> AgentState:
    return {
        "executed": False,
        "stdout": "",
        "stderr": "Execution blocked for safety reasons" + state.get("safety_reason", ""),
        "exit_code": None
    }


# utility function
def route_after_safety(state: AgentState) -> AgentState:
    return "execute_command" if state.get("is_safe", True) else "blocked"