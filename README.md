<div align="center">

# Kiro Agent SDK for Python

**Build AI applications with async/await patterns**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/pypi-v0.1.0-orange.svg)](https://pypi.org/project/kiro-agent-sdk/)

[Getting Started](docs/guide/getting-started.md) |
[API Reference](docs/guide/api-reference.md) |
[Examples](docs/guide/examples.md) |
[User Guide](docs/guide/index.md)

</div>

---

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

## Documentation

Full documentation available in [docs/guide/](docs/guide/):

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/guide/getting-started.md) | Installation, prerequisites, first query |
| [API Reference](docs/guide/api-reference.md) | Complete API documentation |
| [Examples](docs/guide/examples.md) | Common use cases with runnable code |
| [Error Handling](docs/guide/error-handling.md) | Error types and handling patterns |
| [Architecture](docs/guide/architecture.md) | How the SDK works |
| [Troubleshooting](docs/guide/troubleshooting.md) | Common issues and solutions |

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
