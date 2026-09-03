from __future__ import annotations

from typing import Optional, TypedDict

class AgentState(TypedDict, total=false):
    prompt: str
    command: str
    explanation: str
    is_sage: bool
    safety_reason: str
    stderr: str
    executed: bool
    exit_code: Optional[int]