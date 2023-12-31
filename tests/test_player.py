from uno import generate_default_deck, Player
from copy import deepcopy


def test_play_removes_card_from_hand() -> None:
    player = Player(name="Test player")
    hand = generate_default_deck()
    player.take(deepcopy(hand))

    for i, card in enumerate(hand, start=1):
        assert card in player.hand
        n = player.hand.count(card)
        assert 1 <= n <= 4

        player.play(top_card=card, playable_cards=[card])

        assert len(player.hand) == (len(hand) - i)
        assert player.hand.count(card) == (n - 1)
