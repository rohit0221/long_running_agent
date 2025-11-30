from target_repo.src.utils.validators import validate_email

def test_validate_email():
    assert validate_email("test@example.com") is True
    assert validate_email("") is False