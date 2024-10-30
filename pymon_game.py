from game_loader import GameLoader
import sys


# Main execution
def main():
    game = GameLoader()
    game.start_game(sys.argv)

## Main Programm Start Here
if __name__ == "__main__":
    main()
