import pytest

from calculator import divide


def test_divides_numbers() -> None:
    assert divide(8, 2) == 4


def test_raises_on_zero_division() -> None:
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
