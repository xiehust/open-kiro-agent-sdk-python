# Architecture

## Overview

The Kiro Agent SDK wraps the `kiro-cli` command-line tool via subprocess communication. It does not connect directly to an API—all interactions go through the CLI.

## Components

```
User Code
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  query()                         (kiro_agent_sdk/)      │
│  - One-shot async queries                               │
│  - Auto-manages transport lifecycle                     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  KiroSDKClient                   (kiro_agent_sdk/)      │
│  - Multi-turn conversations (limited)                   │
│  - Async context manager                                │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  KiroSubprocessTransport         (_internal/transport/) │
│  - Spawns kiro-cli subprocess                           │
│  - Passes prompt as CLI argument                        │
│  - Parses terminal output                               │
└─────────────────────────────────────────────────────────┘
    │
    ▼
    kiro-cli chat --no-interactive --wrap never "prompt"
```

## Communication Flow

1. **Build command**: Transport constructs CLI command with options
   ```
   kiro-cli chat --no-interactive --wrap never --trust-tools Bash,Read "prompt"
   ```

2. **Spawn process**: CLI started with stdout/stderr pipes

3. **Capture output**: Terminal output read from stdout

4. **Strip ANSI codes**: Color/formatting escape sequences removed

5. **Extract response**: Lines starting with `> ` are the assistant's response

6. **Parse message**: Response converted to `AssistantMessage` with `TextBlock` content

7. **Cleanup**: Process terminated (5s graceful timeout, then kill)

## Why This Design

The kiro-cli does not support JSON streaming or a machine-readable output format. The SDK works around this by:

- Passing prompts as command-line arguments (not stdin)
- Parsing formatted terminal output (not JSON)
- Using `--wrap never` for consistent line breaks
- Stripping ANSI escape codes for clean text

**Implications**:
- Multi-turn conversations require CLI enhancements
- Tool use blocks may not be fully captured
- Response parsing depends on CLI output format

## Key Files

| File | Purpose |
|------|---------|
| `query.py` | Simple `query()` function for one-shot queries |
| `client.py` | `KiroSDKClient` class for multi-turn (limited) |
| `types.py` | Message and option dataclasses |
| `_errors.py` | Error class hierarchy |
| `_internal/transport/subprocess_cli.py` | Subprocess management, output parsing |
| `_internal/message_parser.py` | Convert dicts to typed messages |
