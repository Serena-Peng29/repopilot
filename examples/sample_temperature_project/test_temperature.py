from temperature import celsius_to_fahrenheit


def test_converts_freezing_point() -> None:
    assert celsius_to_fahrenheit(0) == 32


def test_converts_boiling_point() -> None:
    assert celsius_to_fahrenheit(100) == 212
