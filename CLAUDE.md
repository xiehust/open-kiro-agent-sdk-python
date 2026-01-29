# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Setup environment
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run all tests
pytest

# Run single test file
pytest tests/test_query.py

# Run tests matching pattern
pytest -k "test_query"

# Type checking (strict mode)
mypy src/

# Lint and auto-fix
ruff check src/ tests/ --fix

# Format code
ruff format src/ tests/
```

## Architecture

This SDK wraps the `kiro-cli` tool via subprocess communication with three API layers:

```
User Code
    ↓
┌─────────────────────────────────────────────────────────┐
│  query()                         (src/query.py)         │
│  - One-shot async queries                               │
│  - Auto-manages transport lifecycle                     │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  KiroSDKClient                   (src/client.py)        │
│  - Multi-turn conversations                             │
│  - Async context manager                                │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  KiroSubprocessTransport         (src/_internal/)       │
│  - Spawns/manages kiro-cli subprocess                   │
│  - JSON message send/receive via stdin/stdout           │
└─────────────────────────────────────────────────────────┘
    ↓
    kiro-cli subprocess (--no-interactive mode)
```

### Key Module Responsibilities

- **types.py**: Dataclasses for messages (AssistantMessage, UserMessage, ToolResultMessage), content blocks (TextBlock, ToolUseBlock, ToolResultBlock), and configuration (KiroAgentOptions)
- **_errors.py**: Error hierarchy (CLINotFoundError, CLIConnectionError, ProcessError, etc.) all inheriting from KiroSDKError
- **_internal/message_parser.py**: Converts JSON from CLI stdout to typed message dataclasses
- **_internal/transport/subprocess_cli.py**: Subprocess lifecycle management, command building, JSON streaming over stdin/stdout

### Data Flow

1. User calls `query()` or uses `KiroSDKClient`
2. Transport builds CLI command with options (tools, session, verbosity)
3. Subprocess spawned with pipes for stdin/stdout/stderr
4. User message serialized as JSON + newline → stdin
5. CLI responses read as JSON lines from stdout → parsed to typed messages
6. Transport ensures graceful shutdown (5s timeout, then kill)

### Testing Approach

All tests use mocking (no real kiro-cli required). Tests mock:
- `asyncio.create_subprocess_exec` for subprocess spawning
- Process stdin/stdout streams with async generators
- Transport layer for higher-level API tests
