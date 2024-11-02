from game_loader import GameLoader
import sys


def main():
    """Main function to start the game."""
    try:
        game = GameLoader()
        game.start(sys.argv)
    except Exception as e:
        print(f"An error occurred: {e}")

# Entry point of the game
if __name__ == "__main__":
    main()
