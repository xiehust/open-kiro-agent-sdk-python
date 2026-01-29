"""Tests for type definitions."""

from kiro_agent_sdk.types import (
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    AssistantMessage,
    UserMessage,
    ToolResultMessage,
)


def test_text_block_creation():
    """Test TextBlock dataclass."""
    block = TextBlock(text="Hello, world!")
    assert block.type == "text"
    assert block.text == "Hello, world!"


def test_tool_use_block_creation():
    """Test ToolUseBlock dataclass."""
    block = ToolUseBlock(
        id="tool-123",
        name="Bash",
        input={"command": "ls"}
    )
    assert block.type == "tool_use"
    assert block.id == "tool-123"
    assert block.name == "Bash"
    assert block.input == {"command": "ls"}


def test_tool_result_block_creation():
    """Test ToolResultBlock dataclass."""
    block = ToolResultBlock(
        tool_use_id="tool-123",
        content="file1.py\nfile2.py",
        is_error=False
    )
    assert block.type == "tool_result"
    assert block.tool_use_id == "tool-123"
    assert block.content == "file1.py\nfile2.py"
    assert block.is_error is False


def test_tool_result_block_with_error():
    """Test ToolResultBlock with error flag."""
    block = ToolResultBlock(
        tool_use_id="tool-456",
        content="Command failed",
        is_error=True
    )
    assert block.is_error is True


def test_assistant_message_creation():
    """Test AssistantMessage with content blocks."""
    message = AssistantMessage(
        content=[
            TextBlock(text="Hello!"),
            ToolUseBlock(id="t1", name="Bash", input={"command": "ls"})
        ]
    )
    assert message.role == "assistant"
    assert len(message.content) == 2
    assert isinstance(message.content[0], TextBlock)
    assert isinstance(message.content[1], ToolUseBlock)


def test_user_message_creation():
    """Test UserMessage with text content."""
    message = UserMessage(content=[TextBlock(text="Hi there")])
    assert message.role == "user"
    assert len(message.content) == 1
    assert message.content[0].text == "Hi there"


def test_tool_result_message_creation():
    """Test ToolResultMessage."""
    message = ToolResultMessage(
        tool_use_id="tool-123",
        content=[TextBlock(text="Success")]
    )
    assert message.role == "tool_result"
    assert message.tool_use_id == "tool-123"
    assert len(message.content) == 1
