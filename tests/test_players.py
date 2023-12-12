from uno import Player, Players


def _generate_test_players(n_players: int = 3) -> list[Player]:
    players = [Player(name=str(i)) for i in range(1, n_players + 1)]
    return Players(players)


def test_players_next() -> None:
    players = _generate_test_players(n_players=3)

    assert players.next().name == "1"
    assert players.next().name == "2"
    assert players.next().name == "3"
    assert players.next().name == "1"


def test_players_skip() -> None:
    players = _generate_test_players(n_players=3)

    assert players.next().name == "1"
    players.skip()  # skipping player 2
    assert players.next().name == "3"


def test_players_skip_after_init() -> None:
    players = _generate_test_players(n_players=3)

    players.skip()  # skipping player 1
    assert players.next().name == "2"
    assert players.next().name == "3"


def test_players_reverse_after_init() -> None:
    players = _generate_test_players(n_players=3)

    players.reverse()  # reversing cycle
    assert players.next().name == "3"
    assert players.next().name == "2"
    assert players.next().name == "1"
    assert players.next().name == "3"


def test_players_reverse_next_reverse() -> None:
    players = _generate_test_players(n_players=4)

    assert players.next().name == "1"
    assert players.next().name == "2"
    players.reverse()  # reversing cycle
    assert players.next().name == "1"
    players.reverse()  # reversing cycle
    assert players.next().name == "2"
    assert players.next().name == "3"
    assert players.next().name == "4"


def test_players_reverse_next_next_reverse() -> None:
    players = _generate_test_players(n_players=4)

    assert players.next().name == "1"
    assert players.next().name == "2"
    players.reverse()  # reversing cycle
    assert players.next().name == "1"
    assert players.next().name == "4"
    players.reverse()  # reversing cycle
    assert players.next().name == "1"
    assert players.next().name == "2"
    assert players.next().name == "3"


def test_players_reverse_next_skip() -> None:
    players = _generate_test_players(n_players=3)

    assert players.next().name == "1"
    assert players.next().name == "2"
    players.reverse()
    assert players.next().name == "1"
    players.skip()  # skipping player 3
    assert players.next().name == "2"
    assert players.next().name == "1"
