"""Subprocess transport for kiro-cli."""

import asyncio
import os

from kiro_agent_sdk._errors import CLINotFoundError
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

    def _build_command(self, options: KiroAgentOptions) -> list[str]:
        """Build CLI command with arguments."""
        cmd = [self._get_cli_path(options), "chat", "--no-interactive"]

        # Add tool configuration
        if options.allowed_tools:
            cmd.extend(["--trust-tools", ",".join(options.allowed_tools)])
        if options.trust_all_tools:
            cmd.append("--trust-all-tools")

        # Add session management
        if options.resume_session:
            cmd.extend(["--resume", options.resume_session])

        # Add verbosity
        if options.verbose:
            cmd.extend(["-v"] * options.verbose)

        return cmd

    async def start(self, options: KiroAgentOptions) -> None:
        """Start kiro-cli subprocess."""
        cmd = self._build_command(options)

        # Determine working directory
        cwd = str(options.cwd) if options.cwd else os.getcwd()

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        except FileNotFoundError as e:
            raise CLINotFoundError(
                f"kiro-cli not found at {cmd[0]}. "
                "Please install kiro-cli or specify cli_path in options."
            ) from e

    async def stop(self) -> None:
        """Stop kiro-cli subprocess gracefully."""
        if not self.process:
            return

        self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            self.process.kill()
            await self.process.wait()
