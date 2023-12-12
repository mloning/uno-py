from typing import Optional
import random
import itertools


COLORS = ("red", "blue", "green", "yellow")
COLOR_CODES = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "wild": "\033[35m",
}


def is_wild(symbol: Optional[str]) -> bool:
    return symbol.startswith("wild") if symbol else False


def is_wild_draw_4(symbol: Optional[str]) -> bool:
    return symbol == "wild-draw-4"


def is_action(symbol: Optional[str]) -> bool:
    return symbol in ("skip", "reverse", "draw-2", "wild-draw-4")


def check_card_args(
    color: Optional[str], number: Optional[str], symbol: Optional[str]
) -> None:
    assert (number is not None) or (symbol is not None)
    if color:
        assert isinstance(color, str)
    if number:
        assert isinstance(number, str)
        assert color is not None
    if symbol:
        assert isinstance(symbol, str)
        if is_wild(symbol):
            assert color is None


class Card:
    def __init__(
        self,
        color: Optional[str] = None,
        number: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> None:
        check_card_args(color=color, number=number, symbol=symbol)
        self.color = color
        self.number = number
        self.symbol = symbol

        self.is_wild = is_wild(symbol)
        self.is_action = is_action(symbol)

        # handle state of wild cards
        self._init_kwargs = {"color": color, "number": number, "symbol": symbol}

    def copy(self):
        return type(self)(**self._init_kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return False

        if self.is_wild:
            return self.symbol == other.symbol
        else:
            return (
                (self.color == other.color)
                and (self.number == other.number)
                and (self.symbol == self.symbol)
            )

    def __repr__(self) -> str:
        color = self.color or "wild"
        color_code = COLOR_CODES[color]
        value = self.number or self.symbol
        return f"{color_code}{value}\033[0m"


Cards = list[Card]


def check_cards(cards: Cards) -> Cards:
    assert isinstance(cards, list)
    assert len(cards) > 0
    for card in cards:
        assert isinstance(card, Card)
    return cards


class Pile:
    def __init__(self) -> None:
        self.cards: Cards = []

    def append(self, card: Card) -> None:
        self.cards.append(card)

    def recycle(self) -> Cards:
        # return all cards in pile except top card
        assert len(self.cards) > 0
        top_card = self.cards.pop(-1)
        cards = [card.copy() for card in self.cards]

        # restart pile with top card
        self.cards.clear()
        self.cards.append(top_card)

        return cards

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, item) -> Card:
        return self.cards[item]


def generate_default_deck() -> Cards:
    """Generate default deck of Uno cards.

    The deck consists of 108 cards in total:

    * four color suits of 25 cards, including one zero, two each of 1 through
        9, and two each of the action cards "skip", "draw-2" and "reverse"
    * eight colorless cards, with four "wild" and "will-draw-4" cards

    Returns
    -------
    Cards
    """
    numbers = [0, *list(range(1, 10)), *list(range(1, 10))]
    action_symbols = ["reverse", "skip", "draw-2"] * 2
    wild_symbols = ["wild", "wild-draw-4"] * 4

    cards = []
    for color in COLORS:
        for number in numbers:
            card = Card(color=color, number=str(number))
            cards.append(card)
        for symbol in action_symbols:
            card = Card(color=color, symbol=symbol)
            cards.append(card)
    for symbol in wild_symbols:
        card = Card(symbol=symbol)
        cards.append(card)

    assert len(cards) == 108
    return cards


class Deck:
    def __init__(self) -> None:
        self.cards = generate_default_deck()
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> Cards:
        assert len(self.cards) >= n
        cards = self.cards[-n:]
        del self.cards[-n:]
        return cards

    def refill(self, cards: Cards) -> None:
        assert len(self.cards) == 0
        self.cards.extend(cards)
        random.shuffle(self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, item) -> Card:
        return self.cards[item]


class Dealer:
    def __init__(self, n_players: int, n_initial_cards: int) -> None:
        self.deck = Deck()
        self.pile = Pile()

        self.n_players = n_players
        self.n_initial_cards = n_initial_cards

    def flip_initial_card(self) -> None:
        card = self.draw(n=1)[0]
        self.discard(card)

    def draw_initial_hands(self) -> list[Cards]:
        hands = []
        for _ in range(self.n_players):
            hand = self.deck.draw(n=self.n_initial_cards)
            hands.append(hand)
        return hands

    def draw(self, n: int = 1) -> Cards:
        n_available = len(self.deck)
        if n <= n_available:
            return self.deck.draw(n=n)
        else:
            # draw all available cards, recyle pile and draw remaining cards
            n_remaining = n - n_available
            all_cards = []
            cards = self.deck.draw(n=n_available)
            all_cards.extend(cards)

            print("Reclying pile ...")
            cards = self.pile.recycle()
            self.deck.refill(cards)

            cards = self.deck.draw(n=n_remaining)
            all_cards.extend(cards)
            return all_cards

    def discard(self, card: Card) -> None:
        assert isinstance(card, Card)
        self.pile.append(card)

    def get_top_card(self) -> Card:
        assert len(self.pile) > 0
        return self.pile[-1]


class _Strategy:
    def select_card(self, legal_cards: Cards, top_card: Card) -> Optional[Card]:
        # TODO use entire game state as input instead of just top_card
        raise NotImplementedError("abstract method")

    def select_color(self) -> str:
        # TODO use entire game state as input instead of just top_card
        raise NotImplementedError("abstract method")


class RandomStrategy(_Strategy):
    def select_card(self, legal_cards: Cards, top_card: Card) -> Optional[Card]:
        legal_cards = check_cards(legal_cards)
        card = random.choice(legal_cards)
        if card.is_wild:
            card.color = self.select_color()
        return card

    def select_color(self) -> str:
        return random.choice(COLORS)


def filter_legal_cards(cards: Cards, top_card: Card) -> Cards:
    # match color or number or symbol
    # wild cards
    # wild-draw-4 cards if no color match

    legal_cards = []
    wild_draw_4_cards = []
    n_color_matches = 0

    def _is_equal_and_not_none(a: Optional[str], b: Optional[str]) -> bool:
        return (a is not None) and (b is not None) and (a == b)

    for card in cards:
        if is_wild_draw_4(card.symbol):
            wild_draw_4_cards.append(card)
            continue

        is_number = _is_equal_and_not_none(top_card.number, card.number)
        is_symbol = _is_equal_and_not_none(card.symbol, top_card.symbol)
        is_color = _is_equal_and_not_none(card.color, top_card.color)
        is_wild = card.symbol == "wild"
        if is_number or is_color or is_symbol or is_wild:
            legal_cards.append(card)

        if is_color:
            n_color_matches += 1

    if n_color_matches == 0:
        legal_cards.extend(wild_draw_4_cards)

    return legal_cards


class Player:
    def __init__(self, name: str, strategy: Optional[_Strategy] = None) -> None:
        if not strategy:
            strategy = RandomStrategy()

        self.name = name
        self.strategy = strategy

        # player state
        self.hand: Cards = []

    def take(self, cards: Cards) -> None:
        cards = check_cards(cards)
        print(f"Hand before: {self.hand}")
        self.hand.extend(cards)
        print(f"{self.name} took: {cards}")
        print(f"Hand after: {self.hand}")

    def select_card(
        self, top_card: Card, playable_cards: Optional[Cards] = None
    ) -> Optional[Card]:
        if not playable_cards:
            assert len(self.hand) > 0
            playable_cards = self.hand

        legal_cards = filter_legal_cards(cards=self.hand, top_card=top_card)
        if legal_cards:
            card = self.strategy.select_card(legal_cards=legal_cards, top_card=top_card)
            return card
        else:
            return None

    def select_color(self) -> str:
        return self.strategy.select_color()

    def play(
        self, top_card: Card, playable_cards: Optional[Cards] = None
    ) -> Optional[Card]:
        print(f"Hand before: {self.hand}")
        card = self.select_card(top_card=top_card, playable_cards=playable_cards)
        if card:
            self.hand.remove(card)
            print(f"{self.name} played: {card}")
            print(f"Hand after: {self.hand}")
            if len(self.hand) == 1:
                print(f"{self.name}: Uno!")
        return card


def _cycle(values: list, position: Optional[int] = None, is_reversed: bool = False):
    # initial positions
    if not position:
        position = values[0] if is_reversed else values[-1]

    # reverse values
    if is_reversed:
        values = list(reversed(values))

    # rotate list, starting with next value from current position
    start = values.index(position) + 1
    values = values[start:] + values[:start]
    return itertools.cycle(values)


class Players:
    def __init__(self, players: list[Player]) -> None:
        self.players = check_players(players)
        self.position: Optional[Player] = None
        self.is_reversed = False
        self.cycle = _cycle(
            self.players, position=self.position, is_reversed=self.is_reversed
        )

    def next(self) -> Player:
        position = next(self.cycle)
        self.position = position
        return position

    def skip(self) -> None:
        self.next()

    def reverse(self) -> None:
        self.is_reversed = True if not self.is_reversed else False
        self.cycle = _cycle(
            self.players, position=self.position, is_reversed=self.is_reversed
        )

    def first(self) -> Player:
        return self.players[0]


def is_game_over(player: Player) -> bool:
    return len(player.hand) == 0


def check_legal(card: Card, playable_cards: Cards, top_card: Card) -> None:
    legal_cards = filter_legal_cards(cards=playable_cards, top_card=top_card)
    assert card in legal_cards
    if card.is_wild:
        assert card.color is not None


def check_players(players: list[Player]) -> list[Player]:
    assert isinstance(players, list)
    assert 2 <= len(players) <= 5
    for player in players:
        assert isinstance(player, Player)
    return players


def generate_default_players() -> list[Player]:
    names = ("A", "B", "C", "D")
    return [Player(name) for name in names]


def execute_card_action(card: Card, dealer: Dealer, players: Players) -> None:
    assert card.is_action

    # change player cycle
    if card.symbol == "reverse":
        players.reverse()
    elif card.symbol == "skip":
        players.skip()

    # apply penalties
    # TODO implement stacking
    elif card.symbol in ("draw-2", "wild-draw-4"):
        player = players.next()
        print(
            f"Player={player.name} top_card={card=} n_deck={len(dealer.deck)}, "
            f"n_pile={len(dealer.pile)}"
        )
        n_lookup = {"draw-2": 2, "wild-draw-4": 4}
        n = n_lookup[card.symbol]
        cards = dealer.draw(n=n)
        player.take(cards)


class Game:
    def __init__(
        self,
        players: Optional[list[Player]] = None,
        n_initial_cards: int = 7,
    ) -> None:
        if not players:
            players = generate_default_players()

        self.players = Players(players=players)
        n_players = len(players)
        self.dealer = Dealer(n_players=n_players, n_initial_cards=n_initial_cards)

    def run(self) -> None:
        # initialize players' hands
        players = self.players
        dealer = self.dealer

        print("Drawing initial hands ...")
        hands = dealer.draw_initial_hands()
        for player, hand in zip(players.players, hands):
            player.take(hand)

        # first turn
        print("Flip initial card ...")
        dealer.flip_initial_card()
        card = dealer.get_top_card()
        if card.is_wild:
            assert card.color is None
            player = players.first()
            card.color = player.select_color()
        print(
            f"Player=init top_card={card=} n_deck={len(dealer.deck)}, "
            f"n_pile={len(dealer.pile)}"
        )
        if card.is_action:
            execute_card_action(card=card, dealer=dealer, players=players)

        # take turns
        print("Take turns ...")
        while True:
            player = players.next()
            top_card = dealer.get_top_card()
            print(
                f"Player={player.name} {top_card=} n_deck={len(dealer.deck)}, "
                f"n_pile={len(dealer.pile)}"
            )
            playable_cards = [card.copy() for card in player.hand]

            card = player.play(top_card=top_card)

            # if we cannot play any card, we draw a new one; we are allowed to
            # immediately play the new card if possible
            if not card:
                new_card = dealer.draw(n=1)
                player.take(new_card)
                playable_cards = new_card
                card = player.play(top_card=top_card, playable_cards=playable_cards)

            if card:
                check_legal(card=card, top_card=top_card, playable_cards=playable_cards)
                dealer.discard(card)
                if is_game_over(player=player):
                    print(f"Game over. Player: {player.name} won!")
                    break
                if card.is_action:
                    execute_card_action(card=card, dealer=dealer, players=players)
