"""Error classes for Kiro Agent SDK."""


class KiroSDKError(Exception):
    """Base exception for all Kiro SDK errors."""


class CLINotFoundError(KiroSDKError):
    """kiro-cli executable not found."""


class CLIConnectionError(KiroSDKError):
    """Failed to connect to or communicate with CLI process."""


class ProcessError(KiroSDKError):
    """CLI process failed or crashed."""

    def __init__(self, message: str, exit_code: int | None = None):
        super().__init__(message)
        self.exit_code = exit_code


class CLIJSONDecodeError(KiroSDKError):
    """Failed to parse JSON from CLI output."""

    def __init__(self, message: str, raw_output: str):
        super().__init__(message)
        self.raw_output = raw_output


class SessionNotFoundError(KiroSDKError):
    """Requested session ID doesn't exist."""


class ToolPermissionError(KiroSDKError):
    """Tool usage not permitted."""
