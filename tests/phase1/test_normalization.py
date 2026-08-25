from skylark_bi.phase1.normalization import (
    normalize_text,
    normalize_numeric,
    normalize_identifier,
)


def test_normalize_text():
    assert normalize_text(
        "  Energy   Sector "
    ) == "Energy Sector"


def test_normalize_numeric():
    assert normalize_numeric(
        "₹1,25,000"
    ) == 125000


def test_normalize_identifier():
    assert normalize_identifier(
        " owner_001 "
    ) == "OWNER_001"