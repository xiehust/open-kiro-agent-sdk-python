"""Tests for error classes."""

import pytest
from kiro_agent_sdk._errors import (
    KiroSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError,
    SessionNotFoundError,
    ToolPermissionError,
)


def test_base_error():
    """Test base KiroSDKError."""
    error = KiroSDKError("test message")
    assert str(error) == "test message"
    assert isinstance(error, Exception)


def test_cli_not_found_error():
    """Test CLINotFoundError inherits from KiroSDKError."""
    error = CLINotFoundError("CLI not found")
    assert isinstance(error, KiroSDKError)
    assert str(error) == "CLI not found"


def test_process_error_with_exit_code():
    """Test ProcessError stores exit code."""
    error = ProcessError("Process failed", exit_code=1)
    assert error.exit_code == 1
    assert str(error) == "Process failed"


def test_json_decode_error_with_raw_output():
    """Test CLIJSONDecodeError stores raw output."""
    error = CLIJSONDecodeError("Invalid JSON", raw_output="{bad")
    assert error.raw_output == "{bad"
    assert str(error) == "Invalid JSON"
