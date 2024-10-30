from game_loader import GameLoader
import sys


def main():
    """Main function to start the game."""
    game = GameLoader()
    game.start_game(sys.argv)


## Main Programm Start Here
if __name__ == "__main__":
    main()
