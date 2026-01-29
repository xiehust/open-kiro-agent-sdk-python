"""Type definitions for Kiro Agent SDK."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TextBlock:
    """Text content block."""

    text: str
    type: str = field(default="text", init=False)


@dataclass
class ToolUseBlock:
    """Tool use block from assistant."""

    id: str
    name: str
    input: dict[str, Any]
    type: str = field(default="tool_use", init=False)


@dataclass
class ToolResultBlock:
    """Tool result block."""

    tool_use_id: str
    content: str
    is_error: bool = False
    type: str = field(default="tool_result", init=False)


@dataclass
class AssistantMessage:
    """Message from assistant."""

    content: list[TextBlock | ToolUseBlock]
    role: str = field(default="assistant", init=False)


@dataclass
class UserMessage:
    """Message from user."""

    content: list[TextBlock]
    role: str = field(default="user", init=False)


@dataclass
class ToolResultMessage:
    """Tool result message."""

    tool_use_id: str
    content: list[TextBlock]
    role: str = field(default="tool_result", init=False)


@dataclass
class KiroAgentOptions:
    """Configuration options for Kiro Agent."""

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


@dataclass
class SessionInfo:
    """Information about a session."""

    id: str
    created_at: str
    last_active: str
    message_count: int
