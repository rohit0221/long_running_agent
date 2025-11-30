import pytest
from target_repo.src.utils.validators import validate_email, validate_phone

def test_validate_email_valid_basic():
    assert validate_email("user@example.com")

def test_validate_email_valid_complex():
    assert validate_email("john.doe@example.co.uk")

def test_validate_email_invalid_missing_at():
    assert not validate_email("userexample.com")

def test_validate_email_invalid_plus():
    assert not validate_email("user+tag@example.com")

def test_validate_email_empty():
    assert not validate_email("")

def test_validate_phone_valid_plain():
    assert validate_phone("1234567890")

def test_validate_phone_valid_with_delimiters():
    assert validate_phone("(123) 456-7890")

def test_validate_phone_valid_with_country_code():
    assert validate_phone("+1 (555) 123-4567")

def test_validate_phone_invalid_too_few():
    assert not validate_phone("123456789")  # 9 digits

def test_validate_phone_empty():
    assert not validate_phone("")