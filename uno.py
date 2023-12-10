from typing import Optional
import random
import itertools
from dataclasses import dataclass


COLORS = ("red", "blue", "green", "yellow")


def is_wild(symbol: Optional[str]) -> bool:
    if symbol:
        return symbol.startswith("wild")
    else:
        False


def is_wild_draw_4(symbol: Optional[str]) -> bool:
    return symbol == "wild-draw-4"


def is_action(symbol: str) -> bool:
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


@dataclass
class Card:
    def __init__(
        self,
        color: Optional[str] = None,
        number: Optional[str] = None,
        symbol: Optional[str] = None,
    ):
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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.color},{self.number},{self.symbol})"


def check_cards(cards: list[Card]) -> list[Card]:
    assert isinstance(cards, list)
    assert len(cards) > 0
    for card in cards:
        assert isinstance(card, Card)
    return cards


class Pile:
    def __init__(self) -> None:
        self.cards: list[Card] = []

    def append(self, card: Card) -> None:
        self.cards.append(card)

    def recycle(self) -> list[Card]:
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


# The 2018 edition of the game consists of 112 cards: 25 in each of four color suits (red, yellow, green, blue), each suit consisting of one zero, two each of 1 through 9, and two each of the action cards "Skip", "Draw Two", and "Reverse". The deck also contains four "Wild" cards, four "Wild Draw Four", one "Wild Shuffle Hands" and three "Wild Customizable".[2] Sets manufactured prior to 2018 do not contain these last two types of Wild cards, for a total of 108 cards in the deck.[6]
def generate_default_deck() -> list[Card]:
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

    return cards


class Deck:
    def __init__(self) -> None:
        self.cards = generate_default_deck()
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> list[Card]:
        assert len(self.cards) >= n
        cards = self.cards[-n:]
        del self.cards[-n:]
        return cards

    def refill(self, cards: list[Card]) -> None:
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

    def draw_initial_hands(self) -> list[list[Card]]:
        hands = []
        for _ in range(self.n_players):
            hand = self.deck.draw(n=self.n_initial_cards)
            hands.append(hand)
        return hands

    def draw(self, n: int = 1) -> list[Card]:
        n_available = len(self.deck)
        if n <= n_available:
            return self.deck.draw(n=n)
        else:
            # draw all available cards, recyle pile and draw remaining cards
            n_remaining = n - n_available
            all_cards = []
            cards = self.deck.draw(n=n_available)
            all_cards.extend(cards)

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
        top_card = self.pile[-1]
        print(f"Top card: {top_card}")
        return top_card


class _Strategy:
    def select_card(self, legal_cards: list[Card], top_card: Card) -> Optional[Card]:
        # TODO use entire game state as input instead of just top_card
        pass

    def select_color(self) -> str:
        # TODO use entire game state as input instead of just top_card
        pass


class RandomStrategy(_Strategy):
    def select_card(self, legal_cards: list[Card], top_card: Card) -> Optional[Card]:
        legal_cards = check_cards(legal_cards)
        card = random.choice(legal_cards)
        if card.is_wild:
            card.color = self.select_color()
        return card

    def select_color(self) -> str:
        return random.choice(COLORS)


def filter_legal_cards(cards: list[Card], top_card: Card) -> list[Card]:
    # match color or number or symbol
    # wild cards
    # wild-draw-4 cards if no color match

    legal_cards = []
    wild_draw_4_cards = []
    n_color_matches = 0

    def _equal_attr(a: str, b: str) -> bool:
        return (a is not None) and (b is not None) and (a == b)

    for card in cards:
        if is_wild_draw_4(card.symbol):
            wild_draw_4_cards.append(card)
            continue

        is_number = _equal_attr(top_card.number, card.number)
        is_symbol = _equal_attr(card.symbol, top_card.symbol)
        is_color = _equal_attr(card.color, top_card.color)
        if is_number or is_color or is_symbol:
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
        self.hand: list[Card] = []

    def take(self, cards: list[Card]) -> None:
        cards = check_cards(cards)
        self.hand.extend(cards)
        print(f"{self.name} took: {cards}")

    def select_card(
        self, top_card: Card, playable_cards: Optional[list[Card]] = None
    ) -> Optional[Card]:
        assert len(self.hand) > 0
        if not playable_cards:
            playable_cards = self.hand

        legal_cards = filter_legal_cards(cards=self.hand, top_card=top_card)
        if legal_cards:
            card = self.strategy.select_card(legal_cards=legal_cards, top_card=top_card)
            return card

    def select_color(self) -> str:
        return self.strategy.select_color()

    def play(
        self, top_card: Card, playable_cards: Optional[list[Card]] = None
    ) -> Optional[Card]:
        assert self.hand is not None
        card = self.select_card(top_card=top_card, playable_cards=playable_cards)
        if card:
            self.hand.remove(card)
            print(f"{self.name} played: {card}")
            if len(self.hand) == 1:
                print(f"{self.name}: Uno!")
            return card


class Players:
    def __init__(self, players: list[Player]) -> None:
        self.players = check_players(players)
        self.cycle = self._create_cycle(players)

    @staticmethod
    def _create_cycle(players: list[Player]):
        return itertools.cycle(players)

    def reverse(self):
        n_players = len(self.players)
        players = [self.next() for _ in range(n_players)]
        players = reversed(players)
        self.cycle = self._create_cycle(players)
        print("Players reversed")

    def skip(self) -> None:
        player = self.next()
        print(f"{player.name} skipped")

    def first(self) -> Player:
        return self.players[0]

    def next(self) -> Player:
        player = next(self.cycle)
        print(f"{player.name}’s turn ...")
        return player

    def __iter__(self):
        yield from self.players


def is_game_over(player: Player) -> bool:
    return len(player.hand) == 0


def check_legal(card: Card, playable_cards: list[Card], top_card: Card) -> None:
    legal_cards = filter_legal_cards(cards=playable_cards, top_card=top_card)
    assert card in legal_cards
    if card.is_wild:
        assert card.color is not None


def check_players(players: list[Player]) -> list[Player]:
    assert isinstance(players, list)
    assert 2 <= len(players) <= 4
    for player in players:
        assert isinstance(player, Player)
    return players


def generate_default_players() -> list[Player]:
    names = ("A", "B", "C", "D")
    return [Player(name) for name in names]


def execute_card_action(card: Card, dealer: Dealer, players: Players) -> None:
    assert card.is_action

    # players cycle changes
    if card.symbol == "reverse":
        players.reverse()
    elif card.symbol == "skip":
        players.skip()

    player = players.next()

    # player hand changes
    if card.symbol == "draw-2":
        cards = dealer.draw(n=2)
        player.take(cards)
    elif card.symbol == "wild-draw-4":
        cards = dealer.draw(n=4)
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
        for player, hand in zip(players, hands):
            player.take(hand)

        # first turn
        print("First turn ...")
        dealer.flip_initial_card()
        card = dealer.get_top_card()
        if card.is_wild:
            assert card.color is None
            player = players.first()
            card.color = player.select_color()
        if card.is_action:
            execute_card_action(card=card, dealer=dealer, players=players)

        # take turns
        while True:
            # breakpoint()
            player = players.next()
            top_card = dealer.get_top_card()
            playable_cards = [card.copy() for card in player.hand]
            card = player.play(top_card=top_card)
            if card:
                check_legal(card=card, top_card=top_card, playable_cards=playable_cards)
                dealer.discard(card)
                if card.is_action:
                    execute_card_action(card=card, dealer=dealer, players=players)
            else:
                card = dealer.draw(n=1)
                player.take(card)
                card = player.play(top_card=top_card, playable_cards=card)
                if card:
                    check_legal(card=card, top_card=top_card, playable_cards=[card])
                    dealer.discard(card)
                    if card.is_action:
                        execute_card_action(card=card, dealer=dealer, players=players)

            if is_game_over(player=player):
                print(f"{player.name} won!")
                break


# main
if __name__ == "__main__":
    # random.seed(47)
    game = Game()
    game.run()
