# Kiro Agent SDK Python Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python SDK that wraps kiro-cli to provide async, Pythonic API for AI applications

**Architecture:** Subprocess-based communication with kiro-cli in --no-interactive mode, dual API (simple query() + full KiroSDKClient), strong typing with dataclasses

**Tech Stack:** Python 3.10+, asyncio, dataclasses, pytest, mypy, ruff, uv for dependency management

---

## Phase 1: Project Foundation

### Task 1: Project Setup and pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `LICENSE`

**Step 1: Write pyproject.toml with uv**

```toml
[project]
name = "kiro-agent-sdk"
version = "0.1.0"
description = "Python SDK for Kiro Agent - build AI applications with async/await"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Apache-2.0"}
authors = [
    {name = "Kiro SDK Team"}
]
dependencies = [
    "anyio>=4.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "build>=1.0.0",
    "twine>=5.0.0",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
kiro_agent_sdk = ["bin/*", "py.typed"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

**Step 2: Write basic README.md**

```markdown
# Kiro Agent SDK for Python

Python SDK for Kiro Agent. Build AI applications with async/await patterns.

## Installation

```bash
pip install kiro-agent-sdk
```

## Quick Start

```python
import anyio
from kiro_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

## Development

```bash
# Install with uv
uv pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```

## License

Apache 2.0
```

**Step 3: Write LICENSE**

```
Apache License 2.0
[Standard Apache 2.0 license text]
```

**Step 4: Initialize uv environment**

Run: `uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"`
Expected: Virtual environment created and dev dependencies installed

**Step 5: Commit**

```bash
git add pyproject.toml README.md LICENSE
git commit -m "feat: initial project setup with uv

Add pyproject.toml with dependencies, basic README, and Apache license

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 2: Directory Structure

**Files:**
- Create: `src/kiro_agent_sdk/__init__.py`
- Create: `src/kiro_agent_sdk/_version.py`
- Create: `src/kiro_agent_sdk/_cli_version.py`
- Create: `src/kiro_agent_sdk/_internal/__init__.py`
- Create: `src/kiro_agent_sdk/_internal/transport/__init__.py`
- Create: `tests/conftest.py`
- Create: `examples/.gitkeep`
- Create: `scripts/.gitkeep`

**Step 1: Create source directory structure**

Run: `mkdir -p src/kiro_agent_sdk/_internal/transport tests examples scripts`

**Step 2: Write _version.py**

```python
"""Package version."""

__version__ = "0.1.0"
```

**Step 3: Write _cli_version.py**

```python
"""Bundled CLI version."""

CLI_VERSION = "latest"  # Will be set during build
```

**Step 4: Write src/kiro_agent_sdk/__init__.py stub**

```python
"""Kiro Agent SDK for Python."""

from kiro_agent_sdk._version import __version__

__all__ = ["__version__"]
```

**Step 5: Write empty __init__.py files**

Run: `touch src/kiro_agent_sdk/_internal/__init__.py src/kiro_agent_sdk/_internal/transport/__init__.py`

**Step 6: Write tests/conftest.py**

```python
"""Pytest configuration."""

import pytest


@pytest.fixture
def mock_kiro_cli():
    """Mock kiro-cli for testing."""
    pass  # Will implement later
```

**Step 7: Create placeholder files**

Run: `touch examples/.gitkeep scripts/.gitkeep`

**Step 8: Verify structure**

Run: `tree src/ tests/ examples/ scripts/ -L 3`
Expected: Proper directory structure displayed

**Step 9: Commit**

```bash
git add src/ tests/ examples/ scripts/
git commit -m "feat: create project directory structure

Add source layout with internal modules, test directory, and placeholders

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Type System Foundation

### Task 3: Error Classes

**Files:**
- Create: `src/kiro_agent_sdk/_errors.py`
- Create: `tests/test_errors.py`

**Step 1: Write failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_errors.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'kiro_agent_sdk._errors'"

**Step 3: Write minimal implementation**

```python
"""Error classes for Kiro Agent SDK."""


class KiroSDKError(Exception):
    """Base exception for all Kiro SDK errors."""


class CLINotFoundError(KiroSDKError):
    """kiro-cli executable not found."""


class CLIConnectionError(KiroSDKError):
    """Failed to connect to or communicate with CLI process."""


class ProcessError(KiroSDKError):
    """CLI process failed or crashed."""

    def __init__(self, message: str, exit_code: int | None = None):
        super().__init__(message)
        self.exit_code = exit_code


class CLIJSONDecodeError(KiroSDKError):
    """Failed to parse JSON from CLI output."""

    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


class SessionNotFoundError(KiroSDKError):
    """Requested session ID doesn't exist."""


class ToolPermissionError(KiroSDKError):
    """Tool usage not permitted."""
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_errors.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/_errors.py tests/test_errors.py
git commit -m "feat: add error class hierarchy

Implement KiroSDKError base class and specific error types with tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 4: Type Definitions - Content Blocks

**Files:**
- Create: `src/kiro_agent_sdk/types.py`
- Create: `tests/test_types.py`

**Step 1: Write failing test for content blocks**

```python
"""Tests for type definitions."""

from kiro_agent_sdk.types import TextBlock, ToolUseBlock, ToolResultBlock


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_types.py::test_text_block_creation -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation for content blocks**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_types.py -v`
Expected: PASS (4 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/types.py tests/test_types.py
git commit -m "feat: add content block types

Implement TextBlock, ToolUseBlock, and ToolResultBlock with tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 5: Type Definitions - Message Types

**Files:**
- Modify: `src/kiro_agent_sdk/types.py`
- Modify: `tests/test_types.py`

**Step 1: Write failing test for message types**

```python
# Add to tests/test_types.py

from kiro_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ToolResultMessage,
)


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_types.py::test_assistant_message_creation -v`
Expected: FAIL with "ImportError"

**Step 3: Add message types to types.py**

```python
# Add to src/kiro_agent_sdk/types.py

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_types.py -v`
Expected: PASS (7 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/types.py tests/test_types.py
git commit -m "feat: add message types

Implement AssistantMessage, UserMessage, ToolResultMessage with tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 6: Type Definitions - Options and Session

**Files:**
- Modify: `src/kiro_agent_sdk/types.py`
- Modify: `tests/test_types.py`

**Step 1: Write failing test for KiroAgentOptions**

```python
# Add to tests/test_types.py

from pathlib import Path
from kiro_agent_sdk.types import KiroAgentOptions, SessionInfo


def test_kiro_agent_options_defaults():
    """Test KiroAgentOptions with all defaults."""
    options = KiroAgentOptions()
    assert options.system_prompt is None
    assert options.model is None
    assert options.max_turns is None
    assert options.temperature is None
    assert options.allowed_tools is None
    assert options.trust_all_tools is False
    assert options.mcp_servers is None
    assert options.cwd is None
    assert options.cli_path is None
    assert options.verbose == 0
    assert options.resume_session is None


def test_kiro_agent_options_with_values():
    """Test KiroAgentOptions with custom values."""
    options = KiroAgentOptions(
        system_prompt="You are helpful",
        model="claude-opus-4",
        max_turns=5,
        temperature=0.7,
        allowed_tools=["Bash", "Read"],
        trust_all_tools=False,
        cwd=Path("/tmp"),
        verbose=2
    )
    assert options.system_prompt == "You are helpful"
    assert options.model == "claude-opus-4"
    assert options.max_turns == 5
    assert options.temperature == 0.7
    assert options.allowed_tools == ["Bash", "Read"]
    assert options.cwd == Path("/tmp")
    assert options.verbose == 2


def test_session_info_creation():
    """Test SessionInfo dataclass."""
    session = SessionInfo(
        id="sess-123",
        created_at="2024-01-01T00:00:00Z",
        last_active="2024-01-01T01:00:00Z",
        message_count=5
    )
    assert session.id == "sess-123"
    assert session.created_at == "2024-01-01T00:00:00Z"
    assert session.last_active == "2024-01-01T01:00:00Z"
    assert session.message_count == 5
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_types.py::test_kiro_agent_options_defaults -v`
Expected: FAIL with "ImportError"

**Step 3: Add options and session types**

```python
# Add to src/kiro_agent_sdk/types.py

from pathlib import Path


@dataclass
class KiroAgentOptions:
    """Configuration options for Kiro Agent."""

    # Agent configuration
    system_prompt: str | None = None
    model: str | None = None
    max_turns: int | None = None
    temperature: float | None = None

    # Tool configuration
    allowed_tools: list[str] | None = None
    trust_all_tools: bool = False

    # MCP server configuration
    mcp_servers: dict[str, Any] | None = None

    # Working directory
    cwd: str | Path | None = None

    # CLI configuration
    cli_path: str | None = None
    verbose: int = 0

    # Session
    resume_session: str | None = None


@dataclass
class SessionInfo:
    """Information about a session."""

    id: str
    created_at: str
    last_active: str
    message_count: int
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_types.py -v`
Expected: PASS (10 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/types.py tests/test_types.py
git commit -m "feat: add KiroAgentOptions and SessionInfo types

Implement configuration and session types with comprehensive tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: Subprocess Transport Layer

### Task 7: Basic Transport Structure

**Files:**
- Create: `src/kiro_agent_sdk/_internal/transport/subprocess_cli.py`
- Create: `tests/test_transport.py`

**Step 1: Write failing test for transport initialization**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transport.py::test_transport_initialization -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal transport implementation**

```python
"""Subprocess transport for kiro-cli."""

import asyncio
from typing import Any

from kiro_agent_sdk.types import KiroAgentOptions


class KiroSubprocessTransport:
    """Manages kiro-cli subprocess communication."""

    def __init__(self) -> None:
        self.process: asyncio.subprocess.Process | None = None

    def _get_cli_path(self, options: KiroAgentOptions) -> str:
        """Get CLI executable path.

        Priority:
        1. options.cli_path if provided
        2. Bundled CLI (TODO)
        3. System kiro-cli in PATH
        """
        if options.cli_path:
            return options.cli_path

        # TODO: Check for bundled CLI

        return "kiro-cli"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transport.py -v`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/_internal/transport/subprocess_cli.py tests/test_transport.py
git commit -m "feat: add basic subprocess transport structure

Implement KiroSubprocessTransport with CLI path resolution

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 8: Transport Start and Stop

**Files:**
- Modify: `src/kiro_agent_sdk/_internal/transport/subprocess_cli.py`
- Modify: `tests/test_transport.py`

**Step 1: Write failing test for start/stop**

```python
# Add to tests/test_transport.py

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transport.py::test_build_command_basic -v`
Expected: FAIL with "AttributeError: '_build_command'"

**Step 3: Implement start and stop methods**

```python
# Modify src/kiro_agent_sdk/_internal/transport/subprocess_cli.py

import json
import os
from pathlib import Path

from kiro_agent_sdk._errors import CLINotFoundError


class KiroSubprocessTransport:
    """Manages kiro-cli subprocess communication."""

    def __init__(self) -> None:
        self.process: asyncio.subprocess.Process | None = None

    def _get_cli_path(self, options: KiroAgentOptions) -> str:
        """Get CLI executable path."""
        if options.cli_path:
            return options.cli_path
        return "kiro-cli"

    def _build_command(self, options: KiroAgentOptions) -> list[str]:
        """Build CLI command with arguments."""
        cmd = [self._get_cli_path(options), "chat", "--no-interactive"]

        # Add tool configuration
        if options.allowed_tools:
            cmd.extend(["--trust-tools", ",".join(options.allowed_tools)])
        if options.trust_all_tools:
            cmd.append("--trust-all-tools")

        # Add session management
        if options.resume_session:
            cmd.extend(["--resume", options.resume_session])

        # Add verbosity
        if options.verbose:
            cmd.extend(["-v"] * options.verbose)

        return cmd

    async def start(self, options: KiroAgentOptions) -> None:
        """Start kiro-cli subprocess."""
        cmd = self._build_command(options)

        # Determine working directory
        cwd = str(options.cwd) if options.cwd else os.getcwd()

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except FileNotFoundError as e:
            raise CLINotFoundError(
                f"kiro-cli not found at {cmd[0]}. "
                "Please install kiro-cli or specify cli_path in options."
            ) from e

    async def stop(self) -> None:
        """Stop kiro-cli subprocess gracefully."""
        if not self.process:
            return

        self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            self.process.kill()
            await self.process.wait()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transport.py -v`
Expected: PASS (11 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/_internal/transport/subprocess_cli.py tests/test_transport.py
git commit -m "feat: implement transport start and stop methods

Add command building, subprocess spawning, and graceful shutdown

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Task 9: Transport Send and Receive

**Files:**
- Modify: `src/kiro_agent_sdk/_internal/transport/subprocess_cli.py`
- Modify: `tests/test_transport.py`

**Step 1: Write failing test for send/receive**

```python
# Add to tests/test_transport.py

from kiro_agent_sdk._errors import CLIJSONDecodeError


@pytest.mark.asyncio
async def test_send_message():
    """Test sending JSON message to CLI stdin."""
    transport = KiroSubprocessTransport()

    # Mock process with stdin
    mock_stdin = MagicMock()
    mock_stdin.write = MagicMock()
    mock_stdin.drain = AsyncMock()

    mock_process = MagicMock()
    mock_process.stdin = mock_stdin
    transport.process = mock_process

    message = {"role": "user", "content": "Hello"}
    await transport.send_message(message)

    # Verify JSON was written
    mock_stdin.write.assert_called_once()
    written_data = mock_stdin.write.call_args[0][0]
    assert b'"role": "user"' in written_data
    assert b'"content": "Hello"' in written_data
    mock_stdin.drain.assert_awaited_once()


@pytest.mark.asyncio
async def test_receive_messages():
    """Test receiving JSON messages from CLI stdout."""
    transport = KiroSubprocessTransport()

    # Mock process with stdout
    async def mock_stdout():
        yield b'{"role": "assistant", "content": "Hi"}\n'
        yield b'{"role": "assistant", "content": "Bye"}\n'

    mock_process = MagicMock()
    mock_process.stdout = mock_stdout()
    transport.process = mock_process

    messages = []
    async for msg in transport.receive_messages():
        messages.append(msg)

    assert len(messages) == 2
    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] == "Hi"
    assert messages[1]["content"] == "Bye"


@pytest.mark.asyncio
async def test_receive_messages_skips_empty_lines():
    """Test receive_messages skips empty lines."""
    transport = KiroSubprocessTransport()

    async def mock_stdout():
        yield b'{"role": "assistant"}\n'
        yield b'\n'  # Empty line
        yield b'  \n'  # Whitespace only
        yield b'{"role": "user"}\n'

    mock_process = MagicMock()
    mock_process.stdout = mock_stdout()
    transport.process = mock_process

    messages = []
    async for msg in transport.receive_messages():
        messages.append(msg)

    # Should only get 2 messages (empty lines skipped)
    assert len(messages) == 2


@pytest.mark.asyncio
async def test_receive_messages_raises_on_invalid_json():
    """Test receive_messages raises CLIJSONDecodeError on bad JSON."""
    transport = KiroSubprocessTransport()

    async def mock_stdout():
        yield b'{invalid json\n'

    mock_process = MagicMock()
    mock_process.stdout = mock_stdout()
    transport.process = mock_process

    with pytest.raises(CLIJSONDecodeError) as exc_info:
        async for msg in transport.receive_messages():
            pass

    assert "invalid json" in exc_info.value.raw_output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_transport.py::test_send_message -v`
Expected: FAIL with "AttributeError: 'send_message'"

**Step 3: Implement send and receive methods**

```python
# Add to KiroSubprocessTransport class

from collections.abc import AsyncIterator

from kiro_agent_sdk._errors import CLIJSONDecodeError


async def send_message(self, message: dict[str, Any]) -> None:
    """Send JSON message to CLI stdin."""
    if not self.process or not self.process.stdin:
        raise RuntimeError("Process not started")

    data = json.dumps(message) + "\n"
    self.process.stdin.write(data.encode())
    await self.process.stdin.drain()


async def receive_messages(self) -> AsyncIterator[dict[str, Any]]:
    """Stream JSON messages from CLI stdout."""
    if not self.process or not self.process.stdout:
        raise RuntimeError("Process not started")

    async for line in self.process.stdout:
        line_str = line.decode().strip()
        if not line_str:
            continue

        try:
            yield json.loads(line_str)
        except json.JSONDecodeError as e:
            raise CLIJSONDecodeError(
                f"Failed to parse JSON from CLI: {e}",
                raw_output=line_str
            ) from e
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_transport.py -v`
Expected: PASS (15 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/_internal/transport/subprocess_cli.py tests/test_transport.py
git commit -m "feat: implement transport send and receive methods

Add JSON message sending/receiving with error handling

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Message Parser

### Task 10: Message Parser Implementation

**Files:**
- Create: `src/kiro_agent_sdk/_internal/message_parser.py`
- Create: `tests/test_message_parser.py`

**Step 1: Write failing test for message parser**

```python
"""Tests for message parser."""

import pytest
from kiro_agent_sdk._internal.message_parser import parse_message
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
    from kiro_agent_sdk._internal.message_parser import parse_content_block

    block_data = {"type": "unknown", "data": "something"}

    with pytest.raises(ValueError, match="Unknown content block type"):
        parse_content_block(block_data)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_message_parser.py::test_parse_assistant_text_message -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal parser implementation**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_message_parser.py -v`
Expected: PASS (6 tests)

**Step 5: Commit**

```bash
git add src/kiro_agent_sdk/_internal/message_parser.py tests/test_message_parser.py
git commit -m "feat: implement message parser

Add JSON to typed message conversion with comprehensive tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 5: Simple Query API

### Task 11: Query Function Implementation

**Files:**
- Create: `src/kiro_agent_sdk/query.py`
- Create: `tests/test_query.py`
- Modify: `src/kiro_agent_sdk/__init__.py`

**Step 1: Write failing test for query function**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_query.py::test_query_basic -v`
Expected: FAIL with "ImportError: cannot import name 'query'"

**Step 3: Implement query function**

```python
"""Simple query API for Kiro Agent SDK."""

from collections.abc import AsyncIterator
from typing import Any

from kiro_agent_sdk._internal.message_parser import parse_message
from kiro_agent_sdk._internal.transport.subprocess_cli import KiroSubprocessTransport
from kiro_agent_sdk.types import (
    AssistantMessage,
    UserMessage,
    ToolResultMessage,
    KiroAgentOptions,
)


async def query(
    prompt: str,
    options: KiroAgentOptions | None = None,
) -> AsyncIterator[AssistantMessage | UserMessage | ToolResultMessage]:
    """Execute a simple query against Kiro Agent.

    Args:
        prompt: The prompt/question to send
        options: Optional configuration options

    Yields:
        Messages from the agent (assistant, user, tool results)

    Example:
        ```python
        async for message in query(prompt="What is 2 + 2?"):
            print(message)
        ```
    """
    if options is None:
        options = KiroAgentOptions()

    transport = KiroSubprocessTransport()

    try:
        # Start subprocess
        await transport.start(options)

        # Send initial prompt
        await transport.send_message({
            "role": "user",
            "content": prompt
        })

        # Stream responses
        async for message_data in transport.receive_messages():
            message = parse_message(message_data)
            yield message

    finally:
        # Always stop transport
        await transport.stop()
```

**Step 4: Update __init__.py to export query**

```python
# Modify src/kiro_agent_sdk/__init__.py

"""Kiro Agent SDK for Python."""

from kiro_agent_sdk._version import __version__
from kiro_agent_sdk.query import query
from kiro_agent_sdk.types import KiroAgentOptions

__all__ = [
    "__version__",
    "query",
    "KiroAgentOptions",
]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_query.py -v`
Expected: PASS (3 tests)

**Step 6: Commit**

```bash
git add src/kiro_agent_sdk/query.py tests/test_query.py src/kiro_agent_sdk/__init__.py
git commit -m "feat: implement query function

Add simple async query API with transport lifecycle management

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Phase 6: Quick Start Example

### Task 12: Quick Start Example

**Files:**
- Create: `examples/quick_start.py`
- Modify: `README.md`

**Step 1: Write quick start example**

```python
"""Quick start example for Kiro Agent SDK."""

import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    """Run a simple query."""
    print("=== Simple Query ===")
    async for message in query(prompt="What is 2 + 2?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

    print("\n=== Query with Options ===")
    options = KiroAgentOptions(
        system_prompt="You are a helpful math tutor",
        max_turns=1
    )

    async for message in query(prompt="Explain prime numbers", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


if __name__ == "__main__":
    anyio.run(main)
```

**Step 2: Update README with better quick start**

```markdown
# Kiro Agent SDK for Python

Python SDK for Kiro Agent. Build AI applications with async/await patterns.

## Installation

```bash
pip install kiro-agent-sdk
```

**Prerequisites:**
- Python 3.10+
- kiro-cli (installed separately or use bundled version)

## Quick Start

```python
import anyio
from kiro_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

## Basic Usage

### Simple Queries

```python
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock

# Simple query
async for message in query(prompt="Hello Kiro"):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)

# With options
options = KiroAgentOptions(
    system_prompt="You are a helpful assistant",
    max_turns=1,
    allowed_tools=["Bash", "Read"]
)

async for message in query(prompt="List files", options=options):
    print(message)
```

## Examples

See [examples/](examples/) directory for more:
- [quick_start.py](examples/quick_start.py) - Basic usage

## Development

```bash
# Install with uv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```

## License

Apache 2.0
```

**Step 3: Test example runs (manual check)**

Run: `python examples/quick_start.py`
Expected: Would run if kiro-cli is installed (mock for now)

**Step 4: Commit**

```bash
git add examples/quick_start.py README.md
git commit -m "docs: add quick start example

Add runnable example and improve README documentation

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Next Steps

This completes **Phase 1-2** of the implementation (Core Foundation + Simple API). The SDK now has:

✅ Project structure with uv
✅ Type system (messages, blocks, options)
✅ Error hierarchy
✅ Subprocess transport layer
✅ Message parser
✅ Simple `query()` function
✅ Basic tests and examples

**Remaining phases** to implement:

- **Phase 3**: Advanced API (`KiroSDKClient` class)
- **Phase 4**: Session management methods
- **Phase 5**: MCP server support, CLI bundling, comprehensive docs

**Testing notes:**
- Integration tests require actual kiro-cli installation
- Current tests use mocks - real CLI tests come in Phase 3
- Before Phase 3, verify kiro-cli JSON protocol matches assumptions

**Open questions to resolve:**
1. Kiro CLI JSON protocol format (verify with actual CLI)
2. Agent configuration mechanism (temp files vs env vars vs stdin)
3. Session API details (list/resume/delete JSON responses)
4. MCP integration specifics
