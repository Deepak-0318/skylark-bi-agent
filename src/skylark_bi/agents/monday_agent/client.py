"""
Low-level read-only Monday.com GraphQL client.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from .config import MondayConfig
from .errors import (
    MondayAPIError,
    MondayAuthenticationError,
    MondayConnectionError,
    MondayPermissionError,
    MondayRateLimitError,
)


class MondayClient:
    """Read-only client for the Monday GraphQL API."""

    ENDPOINT = "https://api.monday.com/v2"

    def __init__(
        self,
        config: MondayConfig,
    ) -> None:

        self.config = config

        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": config.api_token,
                "Content-Type": "application/json",
                "API-Version": config.api_version,
            }
        )

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        payload = {
            "query": query,
            "variables": variables or {},
        }

        last_error: Exception | None = None

        for attempt in range(
            self.config.max_retries + 1
        ):

            try:

                response = self.session.post(
                    self.ENDPOINT,
                    json=payload,
                    timeout=self.config.timeout_seconds,
                )

                if response.status_code == 401:
                    raise MondayAuthenticationError(
                        "Monday.com authentication failed."
                    )

                if response.status_code == 403:
                    raise MondayPermissionError(
                        "Monday.com permission denied."
                    )

                if response.status_code == 429:
                    raise MondayRateLimitError(
                        "Monday.com rate limit reached."
                    )

                response.raise_for_status()

                body = response.json()

                if body.get("errors"):
                    self._raise_graphql_error(
                        body["errors"]
                    )

                return body.get(
                    "data",
                    {},
                )

            except (
                MondayAuthenticationError,
                MondayPermissionError,
                MondayRateLimitError,
                MondayAPIError,
            ):
                raise

            except requests.RequestException as exc:

                last_error = exc

                if attempt >= self.config.max_retries:
                    break

                time.sleep(
                    min(
                        2 ** attempt,
                        8,
                    )
                )

        raise MondayConnectionError(
            "Unable to connect to Monday.com."
        ) from last_error

    @staticmethod
    def _raise_graphql_error(
        errors: list[dict[str, Any]],
    ) -> None:

        message = (
            errors[0].get(
                "message",
                "Unknown Monday GraphQL error.",
            )
            if errors
            else "Unknown Monday GraphQL error."
        )

        lowered = message.lower()

        if (
            "permission" in lowered
            or "unauthorized" in lowered
            or "forbidden" in lowered
        ):
            raise MondayPermissionError(message)

        if (
            "rate" in lowered
            or "complexity" in lowered
        ):
            raise MondayRateLimitError(message)

        raise MondayAPIError(message)