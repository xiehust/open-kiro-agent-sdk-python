"""Message parser for converting JSON to typed messages."""

from typing import Any

from kiro_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ToolResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


def parse_content_block(block: dict[str, Any]) -> TextBlock | ToolUseBlock | ToolResultBlock:
    """Parse a content block from JSON."""
    block_type = block.get("type")

    if block_type == "text":
        return TextBlock(text=block["text"])
    elif block_type == "tool_use":
        return ToolUseBlock(
            id=block["id"],
            name=block["name"],
            input=block["input"]
        )
    elif block_type == "tool_result":
        return ToolResultBlock(
            tool_use_id=block["tool_use_id"],
            content=block["content"],
            is_error=block.get("is_error", False)
        )
    else:
        raise ValueError(f"Unknown content block type: {block_type}")


def parse_message(
    data: dict[str, Any]
) -> AssistantMessage | UserMessage | ToolResultMessage:
    """Parse a message from JSON."""
    role = data.get("role")

    if role == "assistant":
        content = [parse_content_block(block) for block in data["content"]]
        return AssistantMessage(content=content)
    elif role == "user":
        content = [parse_content_block(block) for block in data["content"]]
        return UserMessage(content=content)
    elif role == "tool_result":
        content = [parse_content_block(block) for block in data["content"]]
        return ToolResultMessage(
            tool_use_id=data["tool_use_id"],
            content=content
        )
    else:
        raise ValueError(f"Unknown message role: {role}")
