import pytest
from datetime import datetime
from src.app import validate_card_number, validate_expiry_date, validate_cvv, main

@pytest.mark.parametrize("card_number, expected", [
    ("4111 1111 1111 1111", True),  # Valid Visa
    ("5500 0000 0000 0004", True),  # Valid Mastercard
    ("3782 8224 6310 005", True),   # Valid Amex
    ("6011 1111 1111 1117", True),  # Valid Discover
    ("1234 5678 9012 3456", False), # Invalid number
    ("1234567890123456", False),     # Invalid Luhn
    ("1234 5678 9012 345", False),  # Too short
    ("1234 5678 9012 34567", False), # Too long
    ("abc1 2345 6789 0123", False),  # Non-digit
    ("", False),                     # Empty
    ("4111111111111111", True),      # Valid without spaces
    ("4111-1111-1111-1111", False),  # Contains non-digit
])
def test_validate_card_number(card_number, expected):
    assert validate_card_number(card_number) == expected

@pytest.mark.parametrize("expiry_date, expected", [
    ("12/25", True),    # Valid future date
    ("01/23", True),    # Valid current year
    ("12/22", False),   # Expired date
    ("00/23", False),   # Invalid month
    ("13/23", False),   # Invalid month
    ("12/00", False),   # Invalid year
    ("12/100", False),  # Invalid year
    ("1/23", False),    # Invalid format
    ("1223", False),    # Invalid format
    ("", False),        # Empty
    ("12/ab", False),   # Non-digit
    ("01/00", False),   # Year 00
    ("12/99", True),    # Year 99 (valid)
])
def test_validate_expiry_date(expiry_date, expected):
    assert validate_expiry_date(expiry_date) == expected

@pytest.mark.parametrize("cvv, expected", [
    ("123", True),      # Valid 3-digit
    ("1234", True),     # Valid 4-digit
    ("12", False),      # Too short
    ("12345", False),   # Too long
    ("abc", False),     # Non-digit
    ("", False),        # Empty
    ("123 ", True),     # With trailing space
    (" 123", True),     # With leading space
])
def test_validate_cvv(cvv, expected):
    assert validate_cvv(cvv.strip()) == expected

def test_validate_expiry_date_current_month():
    current_month = datetime.now().month
    current_year = datetime.now().year % 100
    # Test current month and year (should be valid)
    expiry_date = f"{current_month:02d}/{current_year}"
    assert validate_expiry_date(expiry_date) == True
    # Test previous month (should be invalid)
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    expiry_date = f"{prev_month:02d}/{prev_year}"
    assert validate_expiry_date(expiry_date) == False

def test_validate_card_number_edge_cases():
    # Test minimum length (13 digits)
    assert validate_card_number("1234567890123") == False  # Invalid Luhn
    # Test maximum length (19 digits)
    assert validate_card_number("1234567890123456789") == False  # Invalid Luhn
    # Test with spaces
    assert validate_card_number("4111 1111 1111 1111") == True
    # Test without spaces
    assert validate_card_number("4111111111111111") == True
    # Test with mixed spaces
    assert validate_card_number("4111-1111-1111-1111") == False  # Contains non-digit
    # Test all 1's (valid Luhn)
    assert validate_card_number("1111111111111111") == True
    # Test all 0's (invalid Luhn)
    assert validate_card_number("0000000000000000") == False

def test_validate_expiry_date_edge_cases():
    # Test year 00 (should be invalid)
    assert validate_expiry_date("01/00") == False
    # Test year 99 (should be valid)
    assert validate_expiry_date("12/99") == True
    # Test month 01 (should be valid)
    assert validate_expiry_date("01/25") == True
    # Test month 12 (should be valid)
    assert validate_expiry_date("12/25") == True
    # Test month 00 (should be invalid)
    assert validate_expiry_date("00/25") == False
    # Test month 13 (should be invalid)
    assert validate_expiry_date("13/25") == False

def test_validate_cvv_edge_cases():
    # Test exactly 3 digits
    assert validate_cvv("123") == True
    # Test exactly 4 digits
    assert validate_cvv("1234") == True
    # Test 2 digits (should be invalid)
    assert validate_cvv("12") == False
    # Test 5 digits (should be invalid)
    assert validate_cvv("12345") == False
    # Test with letters (should be invalid)
    assert validate_cvv("abc") == False
    # Test with special characters (should be invalid)
    assert validate_cvv("12@") == False
    # Test empty string (should be invalid)
    assert validate_cvv("") == False
    # Test with spaces (should be invalid)
    assert validate_cvv("1 2 3") == False

def test_main_function():
    # This is a basic test to ensure the main function can be called without errors
    # Since main() is a Streamlit app, we can't test its UI directly in pytest
    # We'll just verify it doesn't raise exceptions
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")
