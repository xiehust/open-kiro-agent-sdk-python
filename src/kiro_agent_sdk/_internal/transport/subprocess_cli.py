"""Subprocess transport for kiro-cli."""

import asyncio

from kiro_agent_sdk.types import KiroAgentOptions


class KiroSubprocessTransport:
    """Manages kiro-cli subprocess communication."""

    def __init__(self) -> None:
        self.process: asyncio.subprocess.Process | None = None

    def _get_cli_path(self, options: KiroAgentOptions) -> str:
        """Get CLI executable path.

        Priority:
        1. options.cli_path if provided
        2. Bundled CLI (TODO)
        3. System kiro-cli in PATH
        """
        if options.cli_path:
            return options.cli_path

        # TODO: Check for bundled CLI

        return "kiro-cli"
