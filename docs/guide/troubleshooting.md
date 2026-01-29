# Troubleshooting

## Query Hangs Indefinitely

**Symptoms**: `query()` never returns, program appears frozen.

**Causes**:
- CLI not outputting expected format
- CLI waiting for input or authentication

**Solutions**:

1. Verify kiro-cli works directly:
   ```bash
   kiro-cli chat "Hello"
   ```

2. Check authentication:
   ```bash
   kiro-cli whoami
   ```

3. Update to latest CLI version:
   ```bash
   kiro-cli update
   ```

## "kiro-cli not found"

**Symptoms**: `CLINotFoundError` raised.

**Causes**:
- kiro-cli not installed
- kiro-cli not in system PATH

**Solutions**:

1. Install kiro-cli following official guide

2. Verify installation:
   ```bash
   which kiro-cli
   kiro-cli --version
   ```

3. Use explicit path:
   ```python
   options = KiroAgentOptions(cli_path="/full/path/to/kiro-cli")
   ```

## Empty Response

**Symptoms**: No messages yielded, or `AssistantMessage` with empty content.

**Causes**:
- CLI output doesn't contain `> ` prefix
- Response format changed in CLI update

**Solutions**:

1. Test CLI directly and check output format:
   ```bash
   kiro-cli chat --no-interactive --wrap never "Hello"
   ```

2. Enable verbose logging:
   ```python
   options = KiroAgentOptions(verbose=2)
   ```

3. Check for CLI version compatibility

## Response Truncated

**Symptoms**: Multi-line response appears cut off.

**Causes**:
- Response parsing stops at credits/time line
- Known limitation of terminal output parsing

**Solutions**:

1. This is a known limitation
2. For complete responses, use CLI directly
3. Check if response contains expected content before truncation point

## Authentication Errors

**Symptoms**: CLI exits with authentication error.

**Solutions**:

1. Login to kiro-cli:
   ```bash
   kiro-cli login
   ```

2. Verify login status:
   ```bash
   kiro-cli whoami
   ```

3. Check credentials haven't expired

## Tool Execution Fails

**Symptoms**: Agent can't use tools, permission errors.

**Solutions**:

1. Enable specific tools:
   ```python
   options = KiroAgentOptions(allowed_tools=["Bash", "Read", "Write"])
   ```

2. Or trust all tools:
   ```python
   options = KiroAgentOptions(trust_all_tools=True)
   ```

## Debugging Tips

### Enable Verbose Output

```python
options = KiroAgentOptions(verbose=2)
```

Verbosity levels:
- `0`: No extra output (default)
- `1`: Some debug info
- `2`: Full debug output

### Test CLI Directly

Before debugging SDK issues, verify the CLI works:

```bash
# Basic test
kiro-cli chat "What is 2+2?"

# With same flags SDK uses
kiro-cli chat --no-interactive --wrap never "What is 2+2?"

# With tools
kiro-cli chat --no-interactive --trust-tools Bash "List files"
```

### Check Process Output

If you need to see raw CLI output, the `ProcessError` exception may contain useful information in its message.

### Common Checks

1. **CLI version**: `kiro-cli --version`
2. **Authentication**: `kiro-cli whoami`
3. **CLI health**: `kiro-cli doctor`
4. **Network**: Ensure internet connectivity
