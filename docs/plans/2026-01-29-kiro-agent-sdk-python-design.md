# Kiro Agent SDK for Python - Design Document

**Date:** 2026-01-29
**Status:** Design Phase
**Purpose:** Python SDK that wraps kiro-cli to provide a Pythonic, async interface for building AI applications

## Overview

The Kiro Agent SDK for Python will provide a developer-friendly wrapper around `kiro-cli`, similar to how Claude Agent SDK wraps Claude Code CLI. The SDK enables Python developers to build AI applications powered by Kiro without dealing with subprocess management or CLI argument construction.

## Goals

- **Pythonic API**: Async/await patterns, type hints, context managers
- **Two interfaces**: Simple `query()` function and full-featured `KiroSDKClient` class
- **Programmatic configuration**: All settings via Python code (no pre-configured agents required)
- **Easy installation**: Bundle kiro-cli with the package
- **Developer friendly**: Strong typing, clear errors, comprehensive examples

## Non-Goals (v1)

- Synchronous API (async only)
- Hooks/callbacks system (can add later if needed)
- Exposing all CLI commands (`translate`, `doctor`, `settings`, etc.)
- In-process SDK MCP servers (external MCP servers only)

## Architecture

### Core Components

```
kiro_agent_sdk/
├── __init__.py           # Public API exports
├── query.py              # Simple query() function
├── client.py             # KiroSDKClient class
├── types.py              # Message types, options, content blocks
├── _errors.py            # Exception hierarchy
├── _version.py           # Package version
├── _cli_version.py       # Bundled CLI version
└── _internal/
    ├── transport/
    │   └── subprocess_cli.py   # CLI process management
    ├── message_parser.py       # Parse JSON stream from CLI
    └── client.py               # Internal client implementation
```

### Communication Flow

1. Python SDK spawns `kiro-cli chat --no-interactive` subprocess
2. SDK sends JSON messages to CLI stdin
3. CLI streams JSON responses via stdout
4. SDK parses and yields Python message objects
5. Process lifecycle managed by context manager or function scope

## API Design

### Simple API: query()

For stateless, one-off queries:

```python
from kiro_agent_sdk import query, KiroAgentOptions

async def main():
    # Simple usage
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

    # With options
    options = KiroAgentOptions(
        system_prompt="You are a helpful assistant",
        max_turns=1,
        allowed_tools=["Bash", "Read"]
    )

    async for message in query(prompt="List Python files", options=options):
        print(message)
```

**Behavior:**
- Spawns new CLI process
- Sends single prompt
- Streams all responses
- Terminates process
- Returns `AsyncIterator[Message]`

### Advanced API: KiroSDKClient

For stateful, multi-turn conversations:

```python
from kiro_agent_sdk import KiroSDKClient, KiroAgentOptions

async def main():
    options = KiroAgentOptions(
        system_prompt="You are a helpful coding assistant",
        allowed_tools=["Read", "Write", "Bash"],
        cwd="/path/to/project"
    )

    async with KiroSDKClient(options=options) as client:
        # Multi-turn conversation
        await client.query("What files are in this project?")
        async for message in client.receive_response():
            print(message)

        await client.query("Read the main.py file")
        async for message in client.receive_response():
            print(message)

        # Session management
        sessions = await client.list_sessions()
        await client.resume_session("session-123")
        await client.delete_session("old-session")
```

**Key Methods:**
- `query(prompt: str)` - Send message to Kiro
- `receive_response() -> AsyncIterator[Message]` - Stream responses
- `list_sessions() -> List[SessionInfo]` - Get saved sessions
- `resume_session(session_id: str)` - Resume conversation
- `delete_session(session_id: str)` - Remove session

## Configuration

### KiroAgentOptions

```python
@dataclass
class KiroAgentOptions:
    # Agent configuration (programmatic, inline)
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    max_turns: Optional[int] = None
    temperature: Optional[float] = None

    # Tool configuration
    allowed_tools: Optional[List[str]] = None  # --trust-tools
    trust_all_tools: bool = False              # --trust-all-tools

    # MCP server configuration
    mcp_servers: Optional[Dict[str, Any]] = None

    # Working directory
    cwd: Optional[Union[str, Path]] = None

    # CLI configuration
    cli_path: Optional[str] = None  # Custom kiro-cli path
    verbose: int = 0                # -v, -vv, -vvv

    # Session (for KiroSDKClient)
    resume_session: Optional[str] = None
```

### MCP Server Configuration

```python
options = KiroAgentOptions(
    mcp_servers={
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
        },
        "github": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": "..."}
        }
    }
)
```

## Type System

### Message Types

```python
@dataclass
class AssistantMessage:
    role: str = "assistant"
    content: List[Union[TextBlock, ToolUseBlock]]

@dataclass
class UserMessage:
    role: str = "user"
    content: List[TextBlock]

@dataclass
class ToolResultMessage:
    role: str = "tool_result"
    tool_use_id: str
    content: List[Union[TextBlock, ErrorBlock]]
```

### Content Blocks

```python
@dataclass
class TextBlock:
    type: str = "text"
    text: str

@dataclass
class ToolUseBlock:
    type: str = "tool_use"
    id: str
    name: str
    input: Dict[str, Any]

@dataclass
class ToolResultBlock:
    type: str = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool = False
```

### Session Types

```python
@dataclass
class SessionInfo:
    id: str
    created_at: str
    last_active: str
    message_count: int
```

## CLI Integration

### Subprocess Transport

The `KiroSubprocessTransport` class manages the CLI process:

```python
class KiroSubprocessTransport:
    async def start(self, options: KiroAgentOptions):
        """Spawn kiro-cli process with options"""
        cmd = [self._get_cli_path(options), "chat", "--no-interactive"]

        # Add tool configuration
        if options.allowed_tools:
            cmd.extend(["--trust-tools", ",".join(options.allowed_tools)])
        if options.trust_all_tools:
            cmd.append("--trust-all-tools")

        # Add session management
        if options.resume_session:
            cmd.extend(["--resume", options.resume_session])

        # Add verbosity
        if options.verbose:
            cmd.extend(["-v"] * options.verbose)

        # Add agent config (see Agent Configuration below)
        if self._has_agent_config(options):
            agent_path = await self._create_temp_agent_config(options)
            cmd.extend(["--agent", agent_path])

        # Spawn process
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=options.cwd or os.getcwd()
        )

    async def send_message(self, message: dict):
        """Send JSON line to CLI stdin"""
        data = json.dumps(message) + "\n"
        self.process.stdin.write(data.encode())
        await self.process.stdin.drain()

    async def receive_messages(self) -> AsyncIterator[dict]:
        """Stream JSON lines from CLI stdout"""
        async for line in self.process.stdout:
            if line.strip():
                yield json.loads(line)

    async def stop(self):
        """Gracefully shutdown CLI process"""
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
```

### Agent Configuration Strategy

Since we want programmatic configuration (no pre-configured agents), we'll use one of these approaches:

**Option 1: Temporary Agent Files**
- Create temporary YAML/JSON agent config from `KiroAgentOptions`
- Pass file path with `--agent /tmp/kiro-agent-xyz.yaml`
- Clean up temp file after process exits

**Option 2: Environment Variables**
- If Kiro supports env vars like `KIRO_SYSTEM_PROMPT`, `KIRO_MODEL`, etc.
- Set env vars when spawning subprocess

**Option 3: Stdin Protocol Extension**
- Send agent configuration as part of initial JSON message
- Requires Kiro CLI to support this

**Decision:** Investigate Kiro's actual capabilities during implementation. Likely start with Option 1 (temp files) as most reliable.

### CLI Bundling

Like Claude Agent SDK, bundle kiro-cli with the Python package:

```python
# scripts/build_wheel.py
def download_cli(version: str, platform: str):
    """Download kiro-cli binary for platform"""
    url = f"https://kiro.dev/releases/{version}/kiro-cli-{platform}"
    # Download and bundle in package data

# pyproject.toml
[tool.setuptools.package-data]
kiro_agent_sdk = ["bin/*"]
```

**CLI Discovery Priority:**
1. `KiroAgentOptions.cli_path` (if provided)
2. Bundled CLI in package
3. System `kiro-cli` in PATH

## Error Handling

### Exception Hierarchy

```python
class KiroSDKError(Exception):
    """Base exception for all Kiro SDK errors"""

class CLINotFoundError(KiroSDKError):
    """kiro-cli executable not found"""

class CLIConnectionError(KiroSDKError):
    """Failed to connect to or communicate with CLI process"""

class ProcessError(KiroSDKError):
    """CLI process failed or crashed"""
    exit_code: Optional[int]

class CLIJSONDecodeError(KiroSDKError):
    """Failed to parse JSON from CLI output"""
    raw_output: str

class SessionNotFoundError(KiroSDKError):
    """Requested session ID doesn't exist"""

class ToolPermissionError(KiroSDKError):
    """Tool usage not permitted"""
```

### Error Handling Strategy

- **Pre-flight validation**: Check CLI exists before starting subprocess
- **Stderr monitoring**: Parse stderr for CLI-specific errors, log warnings
- **Timeout handling**: Configurable timeouts for unresponsive processes
- **Graceful degradation**: Clear error messages with actionable suggestions
- **Resource cleanup**: Ensure processes terminated even on exceptions

### Example Usage

```python
from kiro_agent_sdk import (
    query,
    KiroSDKError,
    CLINotFoundError,
    ProcessError
)

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("Please install kiro-cli or use bundled version")
except ProcessError as e:
    print(f"CLI process failed with exit code {e.exit_code}")
except KiroSDKError as e:
    print(f"SDK error: {e}")
```

## Testing Strategy

### Unit Tests (`tests/`)

- **Message Parser**: Parse various JSON response formats
- **Type Validation**: Ensure types serialize/deserialize correctly
- **Option Building**: Verify CLI arguments constructed correctly
- **Mock Transport**: Test logic without real subprocess

```python
# tests/test_message_parser.py
def test_parse_assistant_message():
    json_line = '{"role": "assistant", "content": [{"type": "text", "text": "Hello"}]}'
    message = parse_message(json_line)
    assert isinstance(message, AssistantMessage)
    assert message.content[0].text == "Hello"
```

### Integration Tests (`tests/test_integration.py`)

- **Subprocess Communication**: Real kiro-cli interaction
- **Query Flow**: End-to-end `query()` function
- **Client Flow**: Multi-turn `KiroSDKClient` conversations
- **Error Scenarios**: CLI crashes, invalid JSON, timeouts

**Requirements:** kiro-cli installed in test environment

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_simple_query():
    async for message in query(prompt="What is 2 + 2?"):
        assert message is not None
```

### E2E Tests (`e2e-tests/`)

- **Real Conversations**: Complete workflows with actual AI responses
- **Tool Usage**: Verify tool execution and results
- **Session Management**: Save, resume, delete sessions
- **MCP Integration**: External MCP servers

```python
# e2e-tests/test_tools.py
@pytest.mark.asyncio
async def test_bash_tool_usage():
    options = KiroAgentOptions(allowed_tools=["Bash"])
    async with KiroSDKClient(options=options) as client:
        await client.query("Run 'echo hello' using bash")
        # Verify tool use and result
```

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
pytest e2e-tests/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Project Structure

```
kiro-agent-sdk-python/
├── src/
│   └── kiro_agent_sdk/
│       ├── __init__.py
│       ├── query.py
│       ├── client.py
│       ├── types.py
│       ├── _errors.py
│       ├── _version.py
│       ├── _cli_version.py
│       └── _internal/
│           ├── __init__.py
│           ├── client.py
│           ├── message_parser.py
│           └── transport/
│               ├── __init__.py
│               └── subprocess_cli.py
├── tests/
│   ├── conftest.py
│   ├── test_types.py
│   ├── test_message_parser.py
│   ├── test_client.py
│   ├── test_transport.py
│   └── test_integration.py
├── e2e-tests/
│   ├── test_conversations.py
│   ├── test_tools.py
│   └── test_sessions.py
├── examples/
│   ├── quick_start.py
│   ├── multi_turn.py
│   ├── tool_usage.py
│   ├── session_management.py
│   └── mcp_servers.py
├── scripts/
│   ├── build_wheel.py
│   ├── download_cli.py
│   └── update_version.py
├── docs/
│   ├── plans/
│   │   └── 2026-01-29-kiro-agent-sdk-python-design.md
│   └── api-reference.md
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Implementation Phases

### Phase 1: Core Foundation
- Project setup (pyproject.toml, directory structure)
- Type definitions (types.py)
- Error classes (_errors.py)
- Basic subprocess transport
- Message parser

### Phase 2: Simple API
- Implement `query()` function
- CLI argument building
- Basic integration tests
- Quick start example

### Phase 3: Advanced API
- Implement `KiroSDKClient`
- Multi-turn conversation support
- Context manager lifecycle
- Tool usage handling

### Phase 4: Session Management
- `list_sessions()`, `resume_session()`, `delete_session()` methods
- Session persistence tests
- Session management examples

### Phase 5: MCP & Polish
- MCP server configuration support
- CLI bundling in package
- Comprehensive documentation
- E2E tests
- Release preparation

## Open Questions

1. **Kiro CLI Protocol**: Need to investigate actual JSON protocol used by `kiro-cli chat --no-interactive`
2. **Agent Config Format**: What format does `--agent` expect? YAML? JSON?
3. **Session API**: How does `--resume`, `--list-sessions`, `--delete-session` work exactly?
4. **MCP Integration**: Does Kiro use standard MCP protocol? Any Kiro-specific extensions?
5. **Tool Response Format**: What's the exact JSON structure for tool uses and results?

## Success Criteria

- [ ] Developers can install with `pip install kiro-agent-sdk`
- [ ] Simple queries work with `query()` function
- [ ] Multi-turn conversations work with `KiroSDKClient`
- [ ] Tool usage (Bash, Read, Write) works correctly
- [ ] Session management (save, resume, delete) functions
- [ ] MCP servers can be configured and used
- [ ] Type hints provide good IDE autocomplete
- [ ] Errors are clear and actionable
- [ ] 80%+ test coverage
- [ ] Comprehensive examples and documentation

## References

- Claude Agent SDK Python: `/home/ubuntu/workspace/open-kiro-agent-sdk-python/claude-agent-sdk-python/`
- Kiro CLI Documentation: https://kiro.dev/docs/cli/reference/cli-commands/
- MCP Protocol: https://modelcontextprotocol.io/
