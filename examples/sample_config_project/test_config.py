from config import get_timeout


def test_reads_configured_timeout() -> None:
    assert get_timeout({"timeout": 10}) == 10


def test_uses_default_timeout() -> None:
    assert get_timeout({}) == 30
