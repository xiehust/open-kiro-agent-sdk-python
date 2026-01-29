"""Tests for subprocess transport."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from kiro_agent_sdk._internal.transport.subprocess_cli import KiroSubprocessTransport
from kiro_agent_sdk.types import KiroAgentOptions


@pytest.mark.asyncio
async def test_transport_initialization():
    """Test transport can be initialized."""
    transport = KiroSubprocessTransport()
    assert transport is not None
    assert transport.process is None


@pytest.mark.asyncio
async def test_get_cli_path_from_options():
    """Test CLI path resolution from options."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions(cli_path="/custom/path/kiro")

    path = transport._get_cli_path(options)
    assert path == "/custom/path/kiro"


@pytest.mark.asyncio
async def test_get_cli_path_default():
    """Test default CLI path resolution."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions()

    path = transport._get_cli_path(options)
    # Should fall back to "kiro-cli" in PATH
    assert path == "kiro-cli"


@pytest.mark.asyncio
async def test_build_command_basic():
    """Test building basic CLI command."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions()

    cmd = transport._build_command(options)
    assert cmd == ["kiro-cli", "chat", "--no-interactive"]


@pytest.mark.asyncio
async def test_build_command_with_tools():
    """Test building command with allowed tools."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions(allowed_tools=["Bash", "Read", "Write"])

    cmd = transport._build_command(options)
    assert "kiro-cli" in cmd
    assert "chat" in cmd
    assert "--no-interactive" in cmd
    assert "--trust-tools" in cmd
    # Should have comma-separated tools after --trust-tools
    trust_tools_idx = cmd.index("--trust-tools")
    assert cmd[trust_tools_idx + 1] == "Bash,Read,Write"


@pytest.mark.asyncio
async def test_build_command_with_trust_all():
    """Test building command with trust_all_tools."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions(trust_all_tools=True)

    cmd = transport._build_command(options)
    assert "--trust-all-tools" in cmd


@pytest.mark.asyncio
async def test_build_command_with_verbose():
    """Test building command with verbosity."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions(verbose=2)

    cmd = transport._build_command(options)
    # Should have two -v flags
    assert cmd.count("-v") == 2


@pytest.mark.asyncio
async def test_start_creates_process():
    """Test start() spawns subprocess."""
    transport = KiroSubprocessTransport()
    options = KiroAgentOptions()

    # Mock subprocess creation
    mock_process = MagicMock()
    mock_process.stdin = MagicMock()
    mock_process.stdout = MagicMock()
    mock_process.stderr = MagicMock()

    with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_create:
        await transport.start(options)

        assert transport.process == mock_process
        mock_create.assert_called_once()
        # Verify command args
        call_args = mock_create.call_args[0]
        assert "kiro-cli" in call_args
        assert "chat" in call_args


@pytest.mark.asyncio
async def test_stop_terminates_process():
    """Test stop() terminates subprocess gracefully."""
    transport = KiroSubprocessTransport()

    # Mock process
    mock_process = MagicMock()
    mock_process.terminate = MagicMock()
    mock_process.wait = AsyncMock(return_value=0)
    transport.process = mock_process

    await transport.stop()

    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_awaited_once()


@pytest.mark.asyncio
async def test_stop_kills_if_timeout():
    """Test stop() kills process if termination times out."""
    transport = KiroSubprocessTransport()

    # Mock process that doesn't terminate
    mock_process = MagicMock()
    mock_process.terminate = MagicMock()
    mock_process.kill = MagicMock()

    async def wait_timeout():
        await asyncio.sleep(10)  # Longer than timeout

    mock_process.wait = AsyncMock(side_effect=wait_timeout)
    transport.process = mock_process

    await transport.stop()

    mock_process.terminate.assert_called_once()
    mock_process.kill.assert_called_once()
