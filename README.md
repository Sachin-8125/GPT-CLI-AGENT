# GPT-CLI-AGENT

A natural-language-to-CLI agent powered by OpenAI and LangGraph. Describe what you want to do in plain English, and the agent generates a Windows-compatible (or PowerShell Core) command, screens it for safety, and — with your confirmation — executes it.

## Features

- **Natural language in, CLI command out** — backed by OpenAI (default: `gpt-4o-mini`).
- **LangGraph workflow** — a 4-node graph: generate → safety screen → (execute | block).
- **Human-in-the-loop** — the graph interrupts before execution so you can confirm (or skip) every command.
- **Safety guardrails** — regex-based scanner blocks destructive patterns (`format`, `del /s /q`, `rmdir /s`, `Remove-Item -Recurse`, `diskpart`, `shutdown`, `reg delete`, and more).
- **Cross-platform shell resolution** — picks the best available shell: `pwsh` (preferred) → `powershell` → `cmd` on Windows, and requires `pwsh` on Linux/macOS.
- **Two usage modes** — one-shot requests or an interactive REPL.
- **Docker-ready** — preconfigured Dockerfile + docker-compose for reproducible runs.

## Architecture

```
prompt → [generate_command] → [screen_command] ──safe──► [execute_command] ──► END
                                             │
                                             └─unsafe─► [blocked] ──► END
                                     (interrupt before execute for user confirmation)
```

See [agent/graph.py](file:///c:/AI-Projects/GPT-CLI-AGENT/agent/graph.py) for the graph definition, [agent/nodes.py](file:///c:/AI-Projects/GPT-CLI-AGENT/agent/nodes.py) for node logic, and [agent/safety.py](file:///c:/AI-Projects/GPT-CLI-AGENT/agent/safety.py) for the pattern list.

## Prerequisites

| Dependency | Required | Notes |
|---|---|---|
| Python | ≥ 3.11 | LangGraph needs modern Python |
| PowerShell Core (`pwsh`) | On Linux/macOS | On Windows, built-in PowerShell or `cmd.exe` works too |
| OpenAI API key | Yes | Set in `.env` as `OPENAI_API_KEY` |

## Local Setup

1. **Clone** and enter the repo.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create `.env`** next to `requirements.txt`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   MODEL_NAME=gpt-4o-mini
   ```
   `MODEL_NAME` is optional; defaults to `gpt-4o-mini` if unset.

## Usage

Entry point: [main.py](file:///c:/AI-Projects/GPT-CLI-AGENT/main.py).

### Interactive REPL (default)

```bash
python main.py
```

Type requests in natural language. Type `exit`, `quit`, or `q` to leave.

```
WinCliAgent - type a request, or 'exit' to quit.

> list all .py files in this project

 command: Get-ChildItem -Recurse -Filter *.py | Select-Object FullName
   details: Recursively finds all .py files and shows their full paths.

Run this command? (y/N) y
```

### One-shot request

```bash
python main.py "show the current IP address"
```

The agent prints the generated command, asks for confirmation, then runs it.

### Auto-execute (skip confirmation)

Use with caution — bypasses the yes/no prompt:

```bash
python main.py --auto "echo hello world"
```

Combine with a prompt:
```bash
python main.py --auto "list files sorted by size descending"
```

### Flags

| Flag | Description |
|---|---|
| `prompt` (positional, `*`) | One or more words forming the request. Omit for REPL. |
| `--auto` | Skip the `Run this command? (y/N)` prompt. |

## Safety

The scanner in [agent/safety.py](file:///c:/AI-Projects/GPT-CLI-AGENT/agent/safety.py) matches commands case-insensitively against a deny-list of dangerous patterns. Blocked commands still go through the graph — they just route to the `blocked` node instead of `execute_command`, and the reason is printed in the terminal.

You should still **always review the generated command** before confirming. The guardrails are best-effort, not a substitute for human judgment.

## Docker

### Build + run with Docker Compose (recommended)

The container image is based on `python:3.11-slim-bookworm` and bundles PowerShell 7.4.6 from Microsoft's official repo.

```bash
# Build the image and start the interactive REPL
docker compose run --rm agent
```

Other useful invocations:
```bash
# One-shot request with confirmation
docker compose run --rm agent python main.py "list files in /app"

# Auto-execute
docker compose run --rm agent python main.py --auto "echo hello from container"

# Drop into bash inside the container
docker compose run --rm agent bash
```

The local project directory is bind-mounted at `/app`, so code edits take effect without rebuilding. Remember your `.env` file must exist locally — it's loaded via `env_file:` in the compose config.

### Plain Docker

```bash
docker build -t wincliagent:latest .
docker run --rm -it --env-file .env -v "$(pwd):/app" wincliagent:latest python main.py
```

## Project Structure

```
GPT-CLI-AGENT/
├── agent/
│   ├── executor.py   # Shell resolver + subprocess runner with timeouts
│   ├── graph.py      # LangGraph workflow, thread config, runner
│   ├── llm.py        # OpenAI client + JSON-response parsing
│   ├── nodes.py      # Graph node implementations + router
│   ├── safety.py     # Dangerous-pattern scanner
│   └── state.py      # TypedDict state schema
├── .gitignore
├── .env              # (you create this)
├── Dockerfile
├── docker-compose.yml
├── main.py           # CLI entry point (argparse + REPL)
├── README.md
└── requirements.txt
```

## Dependencies

Defined in [requirements.txt](file:///c:/AI-Projects/GPT-CLI-AGENT/requirements.txt):

- `langgraph` — orchestration + human-in-the-loop interrupts
- `langchain-openai` — OpenAI chat model wrapper
- `langchain-core` — base message types
- `python-dotenv` — `.env` file loader

## License

Use at your own risk. The authors are not liable for any commands executed by this tool.
