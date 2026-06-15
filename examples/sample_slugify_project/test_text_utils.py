from text_utils import slugify


def test_slugifies_title() -> None:
    assert slugify(" Hello World ") == "hello-world"


def test_collapses_multiple_spaces() -> None:
    assert slugify("Agent   Bench") == "agent-bench"
