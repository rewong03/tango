
import argparse

from game.game import Game


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    game = Game(debug=args.debug)
    game.run()
