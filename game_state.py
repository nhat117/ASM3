import sys
import random
import datetime

class GameState:
    def __init__(self):
        self.items = {}  # Dictionary to store items and their locations
        self.pymons = {}  # Dictionary to store Pymons' locations and stats
        self.user_pymon = {
            'location': None,
            'stats': {},
            'inventory': []
        }

    def save_game(self, file_path='save2024.csv'):
        print("Saving game...")
        print(f"Items: {self.items}")
        print(f"Pymons: {self.pymons}")
        
        # Serialize the game state to a text file
        with open(file_path, 'w') as file:
            file.write(f"Items: {self.items}\n")
            file.write(f"Pymons: {self.pymons}\n")
            file.write(f"User Pymon: {self.user_pymon}\n")

    def load_game(self, file_path='save2024.csv'):
        # Deserialize the game state from a text file
        with open(file_path, 'r') as file:
            lines = file.readlines()
            self.items = eval(lines[0].split(": ", 1)[1].strip())
            self.pymons = eval(lines[1].split(": ", 1)[1].strip())
            self.user_pymon = eval(lines[2].split(": ", 1)[1].strip())
