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
