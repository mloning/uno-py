from uno import Game
from argparse import ArgumentParser, Namespace


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--seed", type=str, default=None, required=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game = Game(seed=args.seed)
    game.run()


if __name__ == "__main__":
    main()
