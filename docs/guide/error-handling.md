# Error Handling

## Error Hierarchy

All SDK errors inherit from `KiroSDKError`:

```
KiroSDKError (base)
├── CLINotFoundError      # kiro-cli executable not found
├── CLIConnectionError    # Failed to communicate with CLI
├── ProcessError          # CLI process failed or crashed
├── CLIJSONDecodeError    # Failed to parse CLI output
├── SessionNotFoundError  # Session ID doesn't exist
└── ToolPermissionError   # Tool usage not permitted
```

## Common Errors

### CLINotFoundError

**When**: kiro-cli is not installed or not in PATH.

```python
from kiro_agent_sdk._errors import CLINotFoundError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError as e:
    print(f"CLI not found: {e}")
    print("Install kiro-cli or set cli_path option")
```

**Solutions**:
- Install kiro-cli: Follow Kiro installation guide
- Specify path: `KiroAgentOptions(cli_path="/path/to/kiro-cli")`

### ProcessError

**When**: CLI process crashes or exits unexpectedly.

```python
from kiro_agent_sdk._errors import ProcessError

try:
    async for message in query(prompt="Hello"):
        print(message)
except ProcessError as e:
    print(f"Process failed: {e}")
    print(f"Exit code: {e.exit_code}")
```

**Attributes**:
- `exit_code`: Process exit code (`int | None`)

**Solutions**:
- Check CLI authentication: `kiro-cli whoami`
- Check CLI logs for details
- Verify CLI version compatibility

### CLIJSONDecodeError

**When**: CLI output cannot be parsed (usually indicates version mismatch).

```python
from kiro_agent_sdk._errors import CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLIJSONDecodeError as e:
    print(f"Parse error: {e}")
    print(f"Raw output: {e.raw_output}")
```

**Attributes**:
- `raw_output`: The unparseable output string

**Solutions**:
- Update kiro-cli to latest version
- Check for CLI output format changes

### CLIConnectionError

**When**: Cannot establish communication with CLI process.

**Solutions**:
- Verify kiro-cli is executable
- Check system resources (memory, file handles)

### SessionNotFoundError

**When**: Attempting to resume a non-existent session.

**Solutions**:
- Verify session ID is correct
- Session may have been deleted

### ToolPermissionError

**When**: Agent attempts to use a tool that isn't permitted.

**Solutions**:
- Add tool to `allowed_tools` option
- Use `trust_all_tools=True`

## Handling Pattern

Catch specific errors first, then fall back to base error:

```python
import anyio
from kiro_agent_sdk import query
from kiro_agent_sdk._errors import (
    KiroSDKError,
    CLINotFoundError,
    ProcessError,
)


async def main():
    try:
        async for message in query(prompt="Hello"):
            print(message)
    except CLINotFoundError:
        print("Please install kiro-cli")
    except ProcessError as e:
        print(f"CLI crashed with exit code: {e.exit_code}")
    except KiroSDKError as e:
        print(f"SDK error: {e}")


anyio.run(main)
```
