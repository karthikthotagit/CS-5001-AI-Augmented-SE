import pytest
from src.calculator import add, subtract, multiply, divide

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_mixed_numbers():
    assert add(-1, 1) == 0

def test_add_floats():
    assert add(0.1, 0.2) == pytest.approx(0.3)

def test_subtract_positive_numbers():
    assert subtract(5, 3) == 2

def test_subtract_negative_numbers():
    assert subtract(-1, -1) == 0

def test_subtract_mixed_numbers():
    assert subtract(1, -1) == 2

def test_subtract_floats():
    assert subtract(0.3, 0.1) == pytest.approx(0.2)

def test_multiply_positive_numbers():
    assert multiply(2, 3) == 6

def test_multiply_negative_numbers():
    assert multiply(-2, -3) == 6

def test_multiply_mixed_numbers():
    assert multiply(-2, 3) == -6

def test_multiply_floats():
    assert multiply(0.5, 0.2) == pytest.approx(0.1)

def test_divide_positive_numbers():
    assert divide(6, 3) == 2

def test_divide_negative_numbers():
    assert divide(-6, -3) == 2

def test_divide_mixed_numbers():
    assert divide(-6, 3) == -2

def test_divide_floats():
    assert divide(0.6, 0.3) == pytest.approx(2.0)

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
