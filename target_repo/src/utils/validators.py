import re

def validate_email(email: str) -> bool:
    if not email:
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    # Simple validation: 10-12 digits
    if not phone:
        return False
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 12
