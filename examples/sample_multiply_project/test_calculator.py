from calculator import multiply


def test_multiplies_positive_numbers() -> None:
    assert multiply(2, 3) == 6


def test_multiplies_by_zero() -> None:
    assert multiply(5, 0) == 0
