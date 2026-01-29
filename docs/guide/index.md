# Kiro Agent SDK User Guide

Python SDK for building AI applications with Kiro Agent using async/await patterns.

```python
from kiro_agent_sdk import query

async for message in query(prompt="What is 2 + 2?"):
    print(message)
```

## Guide Contents

- [Getting Started](getting-started.md) - Installation, prerequisites, and your first query
- [API Reference](api-reference.md) - Complete reference for query(), KiroSDKClient, and types
- [Examples](examples.md) - Common use cases with runnable code
- [Error Handling](error-handling.md) - Error types and handling patterns
- [Architecture](architecture.md) - How the SDK works under the hood
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
