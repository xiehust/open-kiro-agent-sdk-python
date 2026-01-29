"""Tests for KiroSDKClient."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kiro_agent_sdk.client import KiroSDKClient
from kiro_agent_sdk.types import KiroAgentOptions


class TestClientInitialization:
    """Test client initialization."""

    def test_client_initialization_with_default_options(self):
        """Test client can be initialized with default options."""
        client = KiroSDKClient()

        assert client is not None
        assert client._options is not None
        assert isinstance(client._options, KiroAgentOptions)
        assert client._transport is None
        assert client._started is False

    def test_client_initialization_with_custom_options(self):
        """Test client can be initialized with custom options."""
        options = KiroAgentOptions(
            system_prompt="You are a test assistant",
            model="claude-3-5-sonnet",
            max_turns=5,
            trust_all_tools=True,
            cwd="/tmp/test",
        )
        client = KiroSDKClient(options=options)

        assert client._options is options
        assert client._options.system_prompt == "You are a test assistant"
        assert client._options.model == "claude-3-5-sonnet"
        assert client._options.max_turns == 5
        assert client._options.trust_all_tools is True
        assert client._options.cwd == "/tmp/test"


class TestContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager_enters_and_exits(self):
        """Test context manager calls start and stop properly."""
        with (
            patch.object(KiroSDKClient, "start", new_callable=AsyncMock) as mock_start,
            patch.object(KiroSDKClient, "stop", new_callable=AsyncMock) as mock_stop,
        ):
            async with KiroSDKClient() as client:
                assert client is not None
                mock_start.assert_awaited_once()

            mock_stop.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager_returns_client_instance(self):
        """Test __aenter__ returns the client instance."""
        with (
            patch.object(KiroSDKClient, "start", new_callable=AsyncMock),
            patch.object(KiroSDKClient, "stop", new_callable=AsyncMock),
        ):
            client = KiroSDKClient()
            result = await client.__aenter__()

            assert result is client

    @pytest.mark.asyncio
    async def test_context_manager_stops_on_exception(self):
        """Test stop is called even when exception occurs."""
        with (
            patch.object(KiroSDKClient, "start", new_callable=AsyncMock),
            patch.object(KiroSDKClient, "stop", new_callable=AsyncMock) as mock_stop,
        ):
            try:
                async with KiroSDKClient():
                    raise ValueError("Test error")
            except ValueError:
                pass

            mock_stop.assert_awaited_once()


class TestStartStop:
    """Test start and stop methods."""

    @pytest.mark.asyncio
    async def test_start_creates_transport(self):
        """Test start() creates and starts transport."""
        client = KiroSDKClient()

        # Mock KiroSubprocessTransport
        mock_transport = MagicMock()
        mock_transport.start = AsyncMock()

        with patch("kiro_agent_sdk.client.KiroSubprocessTransport", return_value=mock_transport):
            await client.start()

            assert client._transport is mock_transport
            assert client._started is True
            mock_transport.start.assert_awaited_once_with(client._options)

    @pytest.mark.asyncio
    async def test_start_uses_custom_options(self):
        """Test start() uses the provided options."""
        options = KiroAgentOptions(
            cli_path="/custom/kiro",
            verbose=2,
        )
        client = KiroSDKClient(options=options)

        mock_transport = MagicMock()
        mock_transport.start = AsyncMock()

        with patch("kiro_agent_sdk.client.KiroSubprocessTransport", return_value=mock_transport):
            await client.start()

            # Verify transport.start was called with the correct options
            mock_transport.start.assert_awaited_once()
            call_args = mock_transport.start.call_args[0]
            assert call_args[0] is options

    @pytest.mark.asyncio
    async def test_start_is_idempotent(self):
        """Test calling start() multiple times is safe."""
        client = KiroSDKClient()

        mock_transport = MagicMock()
        mock_transport.start = AsyncMock()

        with patch("kiro_agent_sdk.client.KiroSubprocessTransport", return_value=mock_transport):
            await client.start()
            await client.start()  # Second call should be ignored

            # Transport should only be created once
            assert mock_transport.start.await_count == 1

    @pytest.mark.asyncio
    async def test_stop_terminates_transport(self):
        """Test stop() terminates transport."""
        client = KiroSDKClient()

        mock_transport = MagicMock()
        mock_transport.start = AsyncMock()
        mock_transport.stop = AsyncMock()

        with patch("kiro_agent_sdk.client.KiroSubprocessTransport", return_value=mock_transport):
            await client.start()
            await client.stop()

            mock_transport.stop.assert_awaited_once()
            assert client._started is False

    @pytest.mark.asyncio
    async def test_stop_without_start_is_safe(self):
        """Test stop() without start() doesn't raise."""
        client = KiroSDKClient()

        # Should not raise
        await client.stop()

        assert client._started is False
        assert client._transport is None

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self):
        """Test calling stop() multiple times is safe."""
        client = KiroSDKClient()

        mock_transport = MagicMock()
        mock_transport.start = AsyncMock()
        mock_transport.stop = AsyncMock()

        with patch("kiro_agent_sdk.client.KiroSubprocessTransport", return_value=mock_transport):
            await client.start()
            await client.stop()
            await client.stop()  # Second call should be safe

            # Stop should only be called once
            assert mock_transport.stop.await_count == 1


class TestExportedFromPackage:
    """Test that KiroSDKClient is properly exported."""

    def test_client_importable_from_package(self):
        """Test KiroSDKClient can be imported from main package."""
        from kiro_agent_sdk import KiroSDKClient as ImportedClient

        assert ImportedClient is KiroSDKClient

    def test_client_in_all_list(self):
        """Test KiroSDKClient is in __all__."""
        import kiro_agent_sdk

        assert "KiroSDKClient" in kiro_agent_sdk.__all__
