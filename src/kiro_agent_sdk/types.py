"""Type definitions for Kiro Agent SDK."""

from dataclasses import dataclass, field
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
