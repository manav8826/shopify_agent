import pytest
from app.utils.validators import (
    validate_store_url, 
    sanitize_input, 
    validate_date_range, 
    validate_api_structure,
    ValidationError
)

def test_validate_store_url():
    assert validate_store_url("https://test.myshopify.com") is True
    assert validate_store_url("http://test.com") is True
    assert validate_store_url("ftp://test.com") is False
    assert validate_store_url("invalid") is False
    assert validate_store_url("") is False

def test_sanitize_input():
    # HTML escaping
    assert sanitize_input("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    
    # Length truncating
    long_text = "a" * 1005
    sanitized = sanitize_input(long_text, max_length=10)
    assert len(sanitized) == 10
    assert sanitized == "aaaaaaaaaa"
    
    # Empty
    assert sanitize_input(None) == ""

def test_validate_date_range():
    assert validate_date_range("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z") is True
    assert validate_date_range("2025-01-01", "2025-01-01") is True
    
    # Start after end
    assert validate_date_range("2025-01-02", "2025-01-01") is False

def test_validate_date_range_invalid():
    with pytest.raises(ValidationError):
        validate_date_range("invalid", "2025-01-01")

def test_validate_api_structure():
    data = {"id": 1, "name": "Test"}
    assert validate_api_structure(data, ["id", "name"]) is True
    assert validate_api_structure(data, ["id", "email"]) is False
