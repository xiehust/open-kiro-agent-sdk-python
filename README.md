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
