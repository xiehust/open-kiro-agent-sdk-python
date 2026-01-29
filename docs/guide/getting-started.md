# Getting Started

## Prerequisites

- Python 3.10+
- kiro-cli installed and authenticated

Verify kiro-cli is working:

```bash
kiro-cli whoami
kiro-cli chat "Hello"
```

## Installation

```bash
pip install kiro-agent-sdk
```

For development:

```bash
pip install kiro-agent-sdk[dev]
```

## Your First Query

```python
import anyio
from kiro_agent_sdk import query
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    async for message in query(prompt="What is 2 + 2?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

The `query()` function returns an async iterator yielding messages. Extract text by checking for `AssistantMessage` and `TextBlock` types.

## Configuring Options

Use `KiroAgentOptions` to customize behavior:

```python
from kiro_agent_sdk import query, KiroAgentOptions

options = KiroAgentOptions(
    system_prompt="You are a helpful coding assistant",
    allowed_tools=["Bash", "Read"],
    max_turns=1,
)

async for message in query(prompt="List Python files", options=options):
    print(message)
```

### Common Options

| Option | Description |
|--------|-------------|
| `system_prompt` | Custom system prompt for the agent |
| `allowed_tools` | List of tools to trust (e.g., `["Bash", "Read"]`) |
| `trust_all_tools` | Trust all tools without confirmation |
| `cwd` | Working directory for the agent |
| `verbose` | Verbosity level (0, 1, or 2) |

See [API Reference](api-reference.md) for all options.
