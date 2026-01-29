"""Tests for query function."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kiro_agent_sdk import query
from kiro_agent_sdk.types import KiroAgentOptions, AssistantMessage, TextBlock


@pytest.mark.asyncio
async def test_query_basic():
    """Test basic query yields messages."""
    # Mock transport
    mock_transport = MagicMock()
    mock_transport.start = AsyncMock()
    mock_transport.send_message = AsyncMock()
    mock_transport.stop = AsyncMock()

    async def mock_receive():
        yield {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]}

    mock_transport.receive_messages = mock_receive

    with patch(
        "kiro_agent_sdk.query.KiroSubprocessTransport",
        return_value=mock_transport
    ):
        messages = []
        async for message in query(prompt="Hi"):
            messages.append(message)

        assert len(messages) == 1
        assert isinstance(messages[0], AssistantMessage)
        assert messages[0].content[0].text == "Hello"

        # Verify transport lifecycle
        mock_transport.start.assert_awaited_once()
        mock_transport.send_message.assert_awaited_once()
        mock_transport.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_with_options():
    """Test query with custom options."""
    mock_transport = MagicMock()
    mock_transport.start = AsyncMock()
    mock_transport.send_message = AsyncMock()
    mock_transport.stop = AsyncMock()

    async def mock_receive():
        yield {"role": "assistant", "content": [{"type": "text", "text": "Done"}]}

    mock_transport.receive_messages = mock_receive

    options = KiroAgentOptions(
        system_prompt="You are helpful",
        max_turns=1
    )

    with patch(
        "kiro_agent_sdk.query.KiroSubprocessTransport",
        return_value=mock_transport
    ):
        messages = []
        async for message in query(prompt="Test", options=options):
            messages.append(message)

        # Verify options were passed to start
        call_args = mock_transport.start.call_args[0]
        assert call_args[0].system_prompt == "You are helpful"
        assert call_args[0].max_turns == 1


@pytest.mark.asyncio
async def test_query_stops_transport_on_error():
    """Test query stops transport even if error occurs."""
    mock_transport = MagicMock()
    mock_transport.start = AsyncMock()
    mock_transport.send_message = AsyncMock(side_effect=RuntimeError("Test error"))
    mock_transport.stop = AsyncMock()

    with patch(
        "kiro_agent_sdk.query.KiroSubprocessTransport",
        return_value=mock_transport
    ):
        with pytest.raises(RuntimeError, match="Test error"):
            async for message in query(prompt="Test"):
                pass

        # Verify stop was called despite error
        mock_transport.stop.assert_awaited_once()
