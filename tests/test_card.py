import pytest
from uno import Card


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (Card("red", "1"), Card("red", "1"), True),
        (Card("blue", "2"), Card("blue", "2"), True),
        (Card("green", "reverse"), Card("green", "reverse"), True),
        (Card("yellow", "skip"), Card("yellow", "skip"), True),
        (Card("green", "1"), Card("red", "1"), False),
        (Card("red", "2"), Card("blue", "2"), False),
        (Card("yellow", "reverse"), Card("green", "reverse"), False),
        (Card("blue", "skip"), Card("yellow", "skip"), False),
        (Card(None, "wild"), Card(None, "wild"), True),
        (Card(None, "wild-draw-4"), Card(None, "wild"), False),
    ],
)
def test_card_equality(a, b, expected) -> None:
    actual = a == b
    assert actual == expected


def test_card_equality_ignores_color_for_wild_cards() -> None:
    a = Card(None, "wild")
    b = Card(None, "wild")
    b.color = "red"
    assert a == b
