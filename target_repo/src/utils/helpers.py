def format_currency(amount: float) -> str:
    return f"${amount:.2f}"

def parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0
