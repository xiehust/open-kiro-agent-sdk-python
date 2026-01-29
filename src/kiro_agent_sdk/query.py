"""Simple query API for Kiro Agent SDK."""

from collections.abc import AsyncIterator

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
