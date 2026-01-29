# API Reference

## query()

Execute a single query against Kiro Agent.

```python
async def query(
    prompt: str,
    options: KiroAgentOptions | None = None,
) -> AsyncIterator[AssistantMessage | UserMessage | ToolResultMessage]
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | `str` | Yes | The prompt to send to the agent |
| `options` | `KiroAgentOptions \| None` | No | Configuration options |

### Returns

`AsyncIterator` yielding message objects. Iterate with `async for`:

```python
async for message in query(prompt="Hello"):
    if isinstance(message, AssistantMessage):
        # Handle assistant response
        pass
```

## KiroSDKClient

Client for multi-turn conversations with Kiro Agent.

> **Note**: Multi-turn conversations are not fully implemented due to CLI constraints. Use `query()` for single interactions.

```python
class KiroSDKClient:
    def __init__(self, options: KiroAgentOptions | None = None) -> None
    async def __aenter__(self) -> KiroSDKClient
    async def __aexit__(...) -> None
    async def start() -> None
    async def stop() -> None
```

### Usage

```python
from kiro_agent_sdk import KiroSDKClient, KiroAgentOptions

options = KiroAgentOptions(system_prompt="You are helpful")

async with KiroSDKClient(options=options) as client:
    # Client is started
    pass
# Client is automatically stopped
```

### Methods

| Method | Description |
|--------|-------------|
| `start()` | Start the client (called automatically by context manager) |
| `stop()` | Stop the client and clean up resources |

## KiroAgentOptions

Configuration options for Kiro Agent.

```python
@dataclass
class KiroAgentOptions:
    # Agent configuration
    system_prompt: str | None = None
    model: str | None = None
    max_turns: int | None = None
    temperature: float | None = None

    # Tool configuration
    allowed_tools: list[str] | None = None
    trust_all_tools: bool = False

    # MCP server configuration
    mcp_servers: dict[str, Any] | None = None

    # Working directory
    cwd: str | Path | None = None

    # CLI configuration
    cli_path: str | None = None
    verbose: int = 0

    # Session
    resume_session: str | None = None
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `system_prompt` | `str \| None` | `None` | Custom system prompt |
| `model` | `str \| None` | `None` | Model to use |
| `max_turns` | `int \| None` | `None` | Maximum agent turns |
| `temperature` | `float \| None` | `None` | Sampling temperature |
| `allowed_tools` | `list[str] \| None` | `None` | Tools to trust |
| `trust_all_tools` | `bool` | `False` | Trust all tools |
| `mcp_servers` | `dict[str, Any] \| None` | `None` | MCP server config |
| `cwd` | `str \| Path \| None` | `None` | Working directory |
| `cli_path` | `str \| None` | `None` | Custom kiro-cli path |
| `verbose` | `int` | `0` | Verbosity (0-2) |
| `resume_session` | `str \| None` | `None` | Session ID to resume |

## Message Types

### AssistantMessage

Response from the assistant.

```python
@dataclass
class AssistantMessage:
    content: list[TextBlock | ToolUseBlock]
    role: str = "assistant"  # Always "assistant"
```

### UserMessage

Message from the user.

```python
@dataclass
class UserMessage:
    content: list[TextBlock]
    role: str = "user"  # Always "user"
```

### ToolResultMessage

Result from tool execution.

```python
@dataclass
class ToolResultMessage:
    tool_use_id: str
    content: list[TextBlock]
    role: str = "tool_result"  # Always "tool_result"
```

## Content Block Types

### TextBlock

Text content.

```python
@dataclass
class TextBlock:
    text: str
    type: str = "text"  # Always "text"
```

### ToolUseBlock

Tool invocation from assistant.

```python
@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]
    type: str = "tool_use"  # Always "tool_use"
```

### ToolResultBlock

Tool execution result.

```python
@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str
    is_error: bool = False
    type: str = "tool_result"  # Always "tool_result"
```
