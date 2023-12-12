from uno import Game
from argparse import ArgumentParser, Namespace
import random


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--seed", type=str, default=None, required=False)
    parser.add_argument("--player", type=str, default=None, required=False)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.seed:
        random.seed(args.seed)

    game = Game(human_player=args.player)
    game.run()


if __name__ == "__main__":
    main()
