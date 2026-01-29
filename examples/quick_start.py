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
