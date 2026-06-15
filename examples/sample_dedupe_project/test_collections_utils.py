from collections_utils import unique_items


def test_removes_duplicates() -> None:
    assert unique_items(["b", "a", "b"]) == ["b", "a"]


def test_preserves_first_seen_order() -> None:
    assert unique_items(["x", "y", "x", "z"]) == ["x", "y", "z"]
