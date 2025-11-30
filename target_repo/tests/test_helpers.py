import pytest
from target_repo.src.utils.helpers import format_currency, parse_int

@pytest.mark.parametrize(
    "amount, expected",
    [
        (0, "$0.00"),
        (2.5, "$2.50"),
        (-3.25, "$-3.25"),
        (3.0, "$3.00"),
    ],
)
def test_format_currency(amount, expected):
    assert format_currency(amount) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("123", 123),
        ("-45", -45),
        (" 42 ", 42),
        ("0", 0),
        ("9999999999999999", 9999999999999999),
        ("1abc", 0),
        ("", 0),
        ("   ", 0),
        ("1.0", 0),
    ],
)
def test_parse_int(value, expected):
    assert parse_int(value) == expected