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
