from uno import generate_default_deck


def test_generate_default_deck() -> None:
    cards = generate_default_deck()
    assert isinstance(cards, list)
    assert len(cards) == 108
