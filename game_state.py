import sys
import random
import datetime
import os
from exceptions import GameError

class GameState:
    def __init__(self):
        self.items = {}  # Dictionary to store items and their locations
        self.pymons = {}  # Dictionary to store Pymons' locations and stats
        self.user_pymon = {
            'location': None,
            'stats': {},
            'inventory': []
        }

    def save_game(self, file_path='save2024.txt'):
        """
        Save the current game state to a file.
        Format:
        [Items]
        item_name,location_name
        [Pymons]
        pymon_name,location_name,stats
        [UserPymon]
        location_name
        stats
        inventory_items
        """
        try:
            with open(file_path, 'w') as file:
                # Save items
                file.write("[Items]\n")
                for item_name, location in self.items.items():
                    file.write(f"{item_name},{location}\n")
                
                # Save pymons
                file.write("[Pymons]\n")
                for pymon_name, data in self.pymons.items():
                    location = data['location']
                    stats = data['stats'] if data['stats'] else "None"
                    file.write(f"{pymon_name},{location},{stats}\n")
                
                # Save user pymon
                file.write("[UserPymon]\n")
                file.write(f"{self.user_pymon['location']}\n")
                file.write(f"{self.user_pymon['stats']}\n")
                file.write(",".join(self.user_pymon['inventory']))

            print(f"Game saved successfully to {file_path}")
            
        except Exception as e:
            raise GameError(f"Failed to save game: {str(e)}")

    def load_game(self, file_path='save2024.txt'):
        """
        Load a game state from a file.
        """
        try:
            if not os.path.exists(file_path):
                raise GameError(f"Save file not found: {file_path}")

            with open(file_path, 'r') as file:
                section = None
                self.items = {}
                self.pymons = {}
                
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line == "[Items]":
                        section = "items"
                    elif line == "[Pymons]":
                        section = "pymons"
                    elif line == "[UserPymon]":
                        section = "user_pymon"
                        user_pymon_lines = []
                    else:
                        if section == "items":
                            item_name, location = line.split(",")
                            self.items[item_name] = location
                        elif section == "pymons":
                            parts = line.split(",")
                            pymon_name = parts[0]
                            location = parts[1]
                            stats = eval(parts[2]) if parts[2] != "None" else None
                            self.pymons[pymon_name] = {
                                "location": location,
                                "stats": stats
                            }
                        elif section == "user_pymon":
                            user_pymon_lines.append(line)
                            if len(user_pymon_lines) == 3:
                                self.user_pymon = {
                                    "location": user_pymon_lines[0],
                                    "stats": eval(user_pymon_lines[1]),
                                    "inventory": user_pymon_lines[2].split(",") if user_pymon_lines[2] else []
                                }

            print(f"Game loaded successfully from {file_path}")
            
        except Exception as e:
            raise GameError(f"Failed to load game: {str(e)}")
