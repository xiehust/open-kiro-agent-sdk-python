# Examples

## Basic Query

Simple question and answer, extracting text from the response.

```python
import anyio
from kiro_agent_sdk import query
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    async for message in query(prompt="What is the capital of France?"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

## Custom System Prompt

Customize the agent's behavior with a system prompt.

```python
import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    options = KiroAgentOptions(
        system_prompt="You are a helpful math tutor. Explain concepts simply."
    )

    async for message in query(prompt="Explain prime numbers", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

## Tool Usage

Enable specific tools for the agent to use.

```python
import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    # Trust specific tools
    options = KiroAgentOptions(
        allowed_tools=["Bash", "Read", "Write"]
    )

    async for message in query(prompt="List files in the current directory", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

To trust all tools without confirmation:

```python
options = KiroAgentOptions(trust_all_tools=True)
```

## Working Directory

Run queries in a specific directory.

```python
import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    options = KiroAgentOptions(
        cwd="/path/to/project",
        allowed_tools=["Read"]
    )

    async for message in query(prompt="Read the README.md file", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

## Processing Multiple Content Blocks

Handle responses with multiple text blocks.

```python
import anyio
from kiro_agent_sdk import query
from kiro_agent_sdk.types import AssistantMessage, TextBlock, ToolUseBlock


async def main():
    async for message in query(prompt="Explain Python decorators"):
        if isinstance(message, AssistantMessage):
            for i, block in enumerate(message.content):
                if isinstance(block, TextBlock):
                    print(f"Text block {i}: {block.text[:100]}...")
                elif isinstance(block, ToolUseBlock):
                    print(f"Tool use: {block.name}")


anyio.run(main)
```

## Custom CLI Path

Use a specific kiro-cli binary.

```python
import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    options = KiroAgentOptions(
        cli_path="/usr/local/bin/kiro-cli"
    )

    async for message in query(prompt="Hello", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```

## Verbose Output for Debugging

Enable verbose output to debug issues.

```python
import anyio
from kiro_agent_sdk import query, KiroAgentOptions
from kiro_agent_sdk.types import AssistantMessage, TextBlock


async def main():
    options = KiroAgentOptions(
        verbose=2  # 0=off, 1=some, 2=all
    )

    async for message in query(prompt="Hello", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


anyio.run(main)
```
