"""
Typed errors for Monday.com integration.
"""


class MondayIntegrationError(Exception):
    """Base Monday integration error."""


class MondayConfigurationError(
    MondayIntegrationError
):
    """Invalid or missing configuration."""


class MondayAuthenticationError(
    MondayIntegrationError
):
    """Authentication failed."""


class MondayPermissionError(
    MondayIntegrationError
):
    """The token lacks required permissions."""


class MondayBoardNotFoundError(
    MondayIntegrationError
):
    """Requested board could not be found."""


class MondayRateLimitError(
    MondayIntegrationError
):
    """Monday API rate limit was reached."""


class MondayAPIError(
    MondayIntegrationError
):
    """Generic Monday API error."""


class MondayConnectionError(
    MondayIntegrationError
):
    """Network or connection failure."""