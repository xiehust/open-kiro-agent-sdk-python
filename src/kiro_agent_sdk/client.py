"""KiroSDKClient for multi-turn conversations."""

from __future__ import annotations

from kiro_agent_sdk._internal.transport.subprocess_cli import KiroSubprocessTransport
from kiro_agent_sdk.types import KiroAgentOptions


class KiroSDKClient:
    """Client for multi-turn conversations with Kiro Agent.

    This client manages the lifecycle of a kiro-cli subprocess and provides
    an async context manager interface for convenient resource management.

    Example:
        async with KiroSDKClient() as client:
            # Use client for multi-turn conversation
            pass

    Example with custom options:
        options = KiroAgentOptions(
            system_prompt="You are a helpful assistant",
            trust_all_tools=True,
        )
        async with KiroSDKClient(options=options) as client:
            # Use client
            pass
    """

    def __init__(self, options: KiroAgentOptions | None = None) -> None:
        """Initialize the client.

        Args:
            options: Configuration options for the agent. If not provided,
                defaults will be used.
        """
        self._options = options or KiroAgentOptions()
        self._transport: KiroSubprocessTransport | None = None
        self._started = False

    async def __aenter__(self) -> KiroSDKClient:
        """Enter async context manager.

        Returns:
            The client instance after starting.
        """
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit async context manager.

        Ensures the client is properly stopped and resources are cleaned up,
        even if an exception occurred.
        """
        await self.stop()

    async def start(self) -> None:
        """Start the client and underlying transport.

        Creates and starts a new subprocess transport for communication
        with kiro-cli. If already started, this method is a no-op.
        """
        if self._started:
            return

        self._transport = KiroSubprocessTransport()
        await self._transport.start(self._options)
        self._started = True

    async def stop(self) -> None:
        """Stop the client and underlying transport.

        Terminates the subprocess and cleans up resources. If not started
        or already stopped, this method is a no-op.
        """
        if not self._started or self._transport is None:
            return

        await self._transport.stop()
        self._started = False
