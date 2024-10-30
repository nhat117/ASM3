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
        self.locations = {}  # Dictionary to store location states
        self.creatures = {}  # Dictionary to store creature states

    def save_game(self, file_path='save2024.csv'):
        """
        Save the current game state to a file.
        Format:
        [Items]
        item_name,location_name,can_be_picked
        [Locations]
        location_name,description,connected_locations
        [Creatures]
        creature_name,description,location_name,is_pymon
        [UserPymon]
        nickname,description
        location_name
        energy,has_immunity,move_count
        inventory_items
        battle_stats
        """
        try:
            with open(file_path, 'w') as file:
                # Save items
                file.write("[Items]\n")
                for item_name, data in self.items.items():
                    location = data.get('location', 'None')
                    can_be_picked = data.get('can_be_picked', True)
                    file.write(f"{item_name},{location},{can_be_picked}\n")
                
                # Save locations
                file.write("[Locations]\n")
                for loc_name, data in self.locations.items():
                    desc = data.get('description', '')
                    connections = data.get('connections', {})
                    connections_str = ';'.join([f"{dir}={loc}" for dir, loc in connections.items()])
                    file.write(f"{loc_name},{desc},{connections_str}\n")
                
                # Save creatures
                file.write("[Creatures]\n")
                for creature_name, data in self.creatures.items():
                    desc = data.get('description', '')
                    location = data.get('location', 'None')
                    is_pymon = data.get('is_pymon', False)
                    file.write(f"{creature_name},{desc},{location},{is_pymon}\n")
                
                # Save user pymon
                file.write("[UserPymon]\n")
                file.write(f"{self.user_pymon.get('nickname', '')},{self.user_pymon.get('description', '')}\n")
                file.write(f"{self.user_pymon.get('location', 'None')}\n")
                
                stats = self.user_pymon.get('stats', {})
                file.write(f"{stats.get('energy', 3)},{stats.get('has_immunity', False)},{stats.get('move_count', 0)}\n")
                
                inventory = self.user_pymon.get('inventory', [])
                file.write(','.join(inventory) + '\n')
                
                battle_stats = stats.get('battle_stats', [])
                for stat in battle_stats:
                    stat_str = f"{stat['timestamp']},{stat['opponent']},{stat['wins']},{stat['draws']},{stat['losses']}"
                    file.write(stat_str + '\n')

            print(f"Game saved successfully to {file_path}")
            
        except Exception as e:
            raise GameError(f"Failed to save game: {str(e)}")

    def load_game(self, file_path='save2024.csv'):
        """
        Load a game state from a file.
        """
        try:
            if not os.path.exists(file_path):
                raise GameError(f"Save file not found: {file_path}")

            with open(file_path, 'r') as file:
                section = None
                self.items = {}
                self.locations = {}
                self.creatures = {}
                battle_stats = []
                
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line == "[Items]":
                        section = "items"
                    elif line == "[Locations]":
                        section = "locations"
                    elif line == "[Creatures]":
                        section = "creatures"
                    elif line == "[UserPymon]":
                        section = "user_pymon"
                        user_pymon_lines = []
                    else:
                        if section == "items":
                            name, location, can_be_picked = line.split(",")
                            self.items[name] = {
                                'location': location,
                                'can_be_picked': can_be_picked.lower() == 'true'
                            }
                        elif section == "locations":
                            name, desc, connections = line.split(",", 2)
                            connections_dict = {}
                            if connections:
                                for conn in connections.split(";"):
                                    if "=" in conn:
                                        dir, loc = conn.split("=")
                                        connections_dict[dir] = loc
                            self.locations[name] = {
                                'description': desc,
                                'connections': connections_dict
                            }
                        elif section == "creatures":
                            name, desc, location, is_pymon = line.split(",")
                            self.creatures[name] = {
                                'description': desc,
                                'location': location,
                                'is_pymon': is_pymon.lower() == 'true'
                            }
                        elif section == "user_pymon":
                            user_pymon_lines.append(line)
                            if len(user_pymon_lines) >= 4:  # Basic data loaded
                                if ',' in line:  # This is a battle stat line
                                    timestamp, opponent, wins, draws, losses = line.split(",")
                                    battle_stats.append({
                                        'timestamp': timestamp,
                                        'opponent': opponent,
                                        'wins': int(wins),
                                        'draws': int(draws),
                                        'losses': int(losses)
                                    })
                                elif len(user_pymon_lines) == 4:  # Process basic data
                                    nickname, description = user_pymon_lines[0].split(",")
                                    location = user_pymon_lines[1]
                                    energy, has_immunity, move_count = user_pymon_lines[2].split(",")
                                    inventory = user_pymon_lines[3].split(",") if user_pymon_lines[3] else []
                                    
                                    self.user_pymon = {
                                        'nickname': nickname,
                                        'description': description,
                                        'location': location,
                                        'stats': {
                                            'energy': int(energy),
                                            'has_immunity': has_immunity.lower() == 'true',
                                            'move_count': int(move_count),
                                            'battle_stats': battle_stats
                                        },
                                        'inventory': inventory
                                    }

            print(f"Game loaded successfully from {file_path}")
            
        except Exception as e:
            raise GameError(f"Failed to load game: {str(e)}")
