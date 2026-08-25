"""
Monday.com integration configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class MondayConfig:
    """Runtime configuration for the Monday integration."""

    api_token: str
    api_version: str = "2026-07"
    deals_board_id: int | None = None
    work_orders_board_id: int | None = None
    timeout_seconds: int = 30
    max_retries: int = 3
    page_size: int = 500

    @classmethod
    def from_environment(cls) -> "MondayConfig":
        token = os.getenv("MONDAY_API_TOKEN")

        if not token:
            raise ValueError(
                "MONDAY_API_TOKEN is not configured."
            )

        deals_board_id = os.getenv(
            "MONDAY_DEALS_BOARD_ID"
        )

        work_orders_board_id = os.getenv(
            "MONDAY_WORK_ORDERS_BOARD_ID"
        )

        return cls(
            api_token=token,
            api_version=os.getenv(
                "MONDAY_API_VERSION",
                "2026-07",
            ),
            deals_board_id=(
                int(deals_board_id)
                if deals_board_id
                else None
            ),
            work_orders_board_id=(
                int(work_orders_board_id)
                if work_orders_board_id
                else None
            ),
            timeout_seconds=int(
                os.getenv(
                    "MONDAY_API_TIMEOUT",
                    "30",
                )
            ),
            max_retries=int(
                os.getenv(
                    "MONDAY_MAX_RETRIES",
                    "3",
                )
            ),
            page_size=min(
                int(
                    os.getenv(
                        "MONDAY_PAGE_SIZE",
                        "500",
                    )
                ),
                500,
            ),
        )