from target_repo.src.utils.helpers import format_currency

def test_format_currency():
    assert format_currency(10.5) == "$10.50"