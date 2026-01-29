"""Tests for message parser."""

import pytest
from kiro_agent_sdk._internal.message_parser import parse_message, parse_content_block
from kiro_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ToolResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)


def test_parse_assistant_text_message():
    """Test parsing assistant message with text."""
    data = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Hello, how can I help?"}
        ]
    }

    message = parse_message(data)
    assert isinstance(message, AssistantMessage)
    assert len(message.content) == 1
    assert isinstance(message.content[0], TextBlock)
    assert message.content[0].text == "Hello, how can I help?"


def test_parse_assistant_with_tool_use():
    """Test parsing assistant message with tool use."""
    data = {
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Let me check that."},
            {
                "type": "tool_use",
                "id": "tool-123",
                "name": "Bash",
                "input": {"command": "ls -la"}
            }
        ]
    }

    message = parse_message(data)
    assert isinstance(message, AssistantMessage)
    assert len(message.content) == 2
    assert isinstance(message.content[0], TextBlock)
    assert isinstance(message.content[1], ToolUseBlock)
    assert message.content[1].id == "tool-123"
    assert message.content[1].name == "Bash"
    assert message.content[1].input["command"] == "ls -la"


def test_parse_user_message():
    """Test parsing user message."""
    data = {
        "role": "user",
        "content": [
            {"type": "text", "text": "What files are here?"}
        ]
    }

    message = parse_message(data)
    assert isinstance(message, UserMessage)
    assert len(message.content) == 1
    assert message.content[0].text == "What files are here?"


def test_parse_tool_result_message():
    """Test parsing tool result message."""
    data = {
        "role": "tool_result",
        "tool_use_id": "tool-123",
        "content": [
            {"type": "text", "text": "file1.py\nfile2.py"}
        ]
    }

    message = parse_message(data)
    assert isinstance(message, ToolResultMessage)
    assert message.tool_use_id == "tool-123"
    assert len(message.content) == 1
    assert message.content[0].text == "file1.py\nfile2.py"


def test_parse_message_unknown_role():
    """Test parsing message with unknown role raises ValueError."""
    data = {"role": "unknown", "content": []}

    with pytest.raises(ValueError, match="Unknown message role"):
        parse_message(data)


def test_parse_content_block_unknown_type():
    """Test parsing content block with unknown type raises ValueError."""
    block_data = {"type": "unknown", "data": "something"}

    with pytest.raises(ValueError, match="Unknown content block type"):
        parse_content_block(block_data)
