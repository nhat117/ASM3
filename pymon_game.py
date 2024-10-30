from game_loader import PymonGameLoader
import sys


# Main execution
def main():
    # Get the singleton instance of PymonGame
    game = PymonGameLoader()
    game.start_game(sys.argv)


if __name__ == "__main__":
    main()
