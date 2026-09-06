from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int

DEFAULT_TIMEOUT = 60

def _resolve_shell(command: str) -> list[str]:
    system = platform.system()

    if system=='Windows':
        if shutil.which("pwsh"):
            return ["pwsh", "-NoProfile", "-Command", command]
        if shutil.which("powershell"):
            return ["powershell", "-NoProfile", "-Command", command]

        return ["cmd", "/c", command]

    pwsh = shutil.which("pwsh")
    if pwsh:
        return [pwsh, "-NoProfile", "-Command", command]

    raise RuntimeError("PowerShell not found")

def run_command(command: str, timeout: int = DEFAULT_TIMEOUT) -> ExecutionResult:
    arg = _resolve_shell(command)

    try:
        completed = subprocess.run(
            argv=arg,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return ExecutionResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode
        )
    
    except subprocess.TimeoutExpired as e:
        return ExecutionResult(
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=1
        )

    except Exception as e:
        return ExecutionResult(
            stdout="",
            stderr=f"An error occured: {str(e)}",
            exit_code=1
        )
