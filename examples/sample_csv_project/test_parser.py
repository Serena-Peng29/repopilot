from parser import parse_csv_line


def test_parses_comma_separated_values() -> None:
    assert parse_csv_line("alpha,beta,gamma") == ["alpha", "beta", "gamma"]


def test_trims_spaces() -> None:
    assert parse_csv_line("alpha, beta") == ["alpha", "beta"]
