"""Tests for subprocess transport."""

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
