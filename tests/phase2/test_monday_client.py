import pytest

from skylark_bi.agents.monday_agent.config import (
    MondayConfig,
)


def test_config_requires_token(
    monkeypatch,
):

    monkeypatch.delenv(
        "MONDAY_API_TOKEN",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="MONDAY_API_TOKEN",
    ):
        MondayConfig.from_environment()


def test_config_reads_environment(
    monkeypatch,
):

    monkeypatch.setenv(
        "MONDAY_API_TOKEN",
        "test-token",
    )

    monkeypatch.setenv(
        "MONDAY_DEALS_BOARD_ID",
        "123",
    )

    config = MondayConfig.from_environment()

    assert config.api_token == "test-token"
    assert config.deals_board_id == 123
    assert config.page_size == 500