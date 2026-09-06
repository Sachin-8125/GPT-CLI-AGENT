from __future__ import annotations
import re
from typing import Tuple

DANGEROUS_PATTERNS = [
    r"\bformat\b",
    r"\bdel\b.*[\\/]\*",
    r"\bdel\b\s+/[sqf]",
    r"\brmdir\b\s+/s",
    r"\brd\b\s+/s",
    r"\bRemove-Item\b.*-Recurse",
    r"\bdiskpart\b",
    r"\bcipher\b\s+/w",
    r"\bshutdown\b",
    r"\bRestart-Computer\b",
    r"\breg\b\s+delete",
    r"\bRemove-Item\b.*[A-Za-z]:\\\*",
    r":\\\s*$",
    r"\bvssadmin\b\s+delete",
    r"\bbcdedit\b",
    r"\bcd\b.*&&.*\bdel\b",
]

def screen_command(command: str) -> Tuple[bool, str]:
    lowered = command.lower()
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return False, f"Command contains dangerous pattern: {pattern}"

    return True, ""
