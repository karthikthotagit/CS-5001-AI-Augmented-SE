import pytest
from unittest.mock import patch, MagicMock
from src.app import is_prime, main

def test_is_prime_with_negative_number():
    assert is_prime(-1) == False
    assert is_prime(-10) == False

def test_is_prime_with_zero():
    assert is_prime(0) == False

def test_is_prime_with_one():
    assert is_prime(1) == False

def test_is_prime_with_two():
    assert is_prime(2) == True

def test_is_prime_with_three():
    assert is_prime(3) == True

def test_is_prime_with_four():
    assert is_prime(4) == False

def test_is_prime_with_five():
    assert is_prime(5) == True

def test_is_prime_with_six():
    assert is_prime(6) == False

def test_is_prime_with_seven():
    assert is_prime(7) == True

def test_is_prime_with_eight():
    assert is_prime(8) == False

def test_is_prime_with_nine():
    assert is_prime(9) == False

def test_is_prime_with_ten():
    assert is_prime(10) == False

def test_is_prime_with_large_prime():
    assert is_prime(7919) == True

def test_is_prime_with_large_non_prime():
    assert is_prime(7920) == False

def test_is_prime_with_even_number():
    assert is_prime(100) == False

def test_is_prime_with_odd_number():
    assert is_prime(99) == False

def test_main_function():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:
        mock_number_input.return_value = 5
        mock_button.return_value = True
        main()
        mock_title.assert_called_once_with("Prime Number Checker")
        mock_number_input.assert_called_once_with("Enter a number to check if it's prime:", min_value=0, step=1)
        mock_button.assert_called_once_with("Check")
        mock_success.assert_called_once_with("5 is a prime number!")

def test_main_function_with_non_prime():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:
        mock_number_input.return_value = 4
        mock_button.return_value = True
        main()
        mock_title.assert_called_once_with("Prime Number Checker")
        mock_number_input.assert_called_once_with("Enter a number to check if it's prime:", min_value=0, step=1)
        mock_button.assert_called_once_with("Check")
        mock_error.assert_called_once_with("4 is not a prime number.")

def test_main_function_with_button_not_clicked():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:
        mock_number_input.return_value = 5
        mock_button.return_value = False
        main()
        mock_title.assert_called_once_with("Prime Number Checker")
        mock_number_input.assert_called_once_with("Enter a number to check if it's prime:", min_value=0, step=1)
        mock_button.assert_called_once_with("Check")
        mock_success.assert_not_called()
        mock_error.assert_not_called()

def test_main_function_with_zero():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:
        mock_number_input.return_value = 0
        mock_button.return_value = True
        main()
        mock_title.assert_called_once_with("Prime Number Checker")
        mock_number_input.assert_called_once_with("Enter a number to check if it's prime:", min_value=0, step=1)
        mock_button.assert_called_once_with("Check")
        mock_error.assert_called_once_with("0 is not a prime number.")

def test_main_function_with_one():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.number_input') as mock_number_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.error') as mock_error:
        mock_number_input.return_value = 1
        mock_button.return_value = True
        main()
        mock_title.assert_called_once_with("Prime Number Checker")
        mock_number_input.assert_called_once_with("Enter a number to check if it's prime:", min_value=0, step=1)
        mock_button.assert_called_once_with("Check")
        mock_error.assert_called_once_with("1 is not a prime number.")
