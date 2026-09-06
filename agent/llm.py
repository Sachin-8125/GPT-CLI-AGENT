from __future__ import annotations

import json
import os
from typing import Tuple

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import OpenAIChat

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")


SYSTEM_PROMPT = """You are an expert Windows system administrator.
Your job: translate the user's natural-language request into a SINGLE Windows CLI command.

Strict rules:
- Produce commands that run on Windows (cmd.exe or Windows PowerShell). NEVER produce
  Unix/Linux/MacOS commands (no `ls`, `grep`, `cat`, `rm -rf`, `sudo`, `apt`, etc.).
- Prefer commands that also work under PowerShell Core (pwsh), since aliases like `dir`,
  `type`, `copy`, `del`, `echo`, `cls`, and cmdlets like `Get-ChildItem`, `Get-Content`,
  `Select-String` behave consistently there.
- Return exactly ONE command (a single line). Do not chain unrelated commands.
- Do not wrap the command in markdown, backticks, or quotes.

Respond ONLY with a JSON object of the form:
{"command": "<the windows command>", "explanation": "<one short sentence"}
"""


def get_llm() -> OpenAIChat:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")

    return OpenAIChat(
        model=MODEL_NAME,
        api_key=api_key,
        temperature=0,
    )


def generate_command(prompt: str) -> Tuple[str, str]:
    llm = get_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT), 
        HumanMessage(content=prompt)
    ]

    response = llm.invoke(messages)

    content = (response.content or "").strip()

    command, explanation = _parse_response(content)

    return command, explanation


def _parse_response(content: str) -> Tuple[str, str]:
    cleaned = content.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        command = data.get("command","").strip()
        explanation = data.get("explanation","").strip()
        return command, explanation
    except json.JSONDecodeError:
        pass

    return cleaned, ""