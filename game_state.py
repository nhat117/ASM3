import sys
import random
import datetime
import os
from exceptions import GameError


class GameState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one GameState instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the game state with items, Pymons, user Pymon, and locations."""
        if not hasattr(self, "_initialized"):  # To prevent reinitialization
            self.items = {}  # Dictionary to store items and their locations
            self.pymons = {}  # Dictionary to store Pymons' locations and stats
            self.user_pymon = {"location": None, "stats": {}, "inventory": []}
            self.bench_pymons = []  # List to store captured Pymons
            self.locations = {}  # Dictionary to store location states
            self.creatures = {}  # Dictionary to store creature states
            self._initialized = True  # Mark as initialized to prevent reinitialization

    def display_setup(self):
        """
        Display the current setup of the game world including locations, connections,
        items, and creatures. This is for testing purposes only.
        """
        print("\n=== Game World Setup ===\n")

        # Display Locations and their connections
        print("=== Locations ===")
        for loc_name, data in self.locations.items():
            print(f"\nLocation: {loc_name}")
            print(f"Description: {data.get('description', '')}")
            print("Connections:")
            connections = data.get("connections", {})
            if connections:
                for direction, connected_loc in connections.items():
                    print(f"  {direction} -> {connected_loc}")
            else:
                print("  No connections")

        # Display Items and their locations
        print("\n=== Items ===")
        for item_name, data in self.items.items():
            location = data.get("location", "Unknown")
            can_be_picked = data.get("can_be_picked", True)
            print(f"\nItem: {item_name}")
            print(f"Location: {location}")
            print(f"Can be picked: {can_be_picked}")

        # Display Creatures and their locations
        print("\n=== Creatures ===")
        for creature_name, data in self.creatures.items():
            print(f"\nCreature: {creature_name}")
            print(f"Description: {data.get('description', '')}")
            print(f"Location: {data.get('location', 'Unknown')}")
            print(f"Is Pymon: {data.get('is_pymon', False)}")

    def save_game(self, file_path="save2024.csv"):
        """
        Save the current game state to a file in the following format:
        [Items], [Locations], [Creatures], [UserPymon], [BenchPymons].
        """
        try:
            with open(file_path, "w") as file:
                self._save_items(file)
                self._save_locations(file)
                self._save_creatures(file)
                self._save_user_pymon(file)
                self._save_bench_pymons(file)

            print(f"Game saved successfully to {file_path}")

        except Exception as e:
            raise GameError(f"Failed to save game: {str(e)}")

    def _save_items(self, file):
        """Save all items to the file."""
        file.write("[Items]\n")
        for item_name, data in self.items.items():
            location = data.get("location", "None")
            can_be_picked = data.get("can_be_picked", True)
            file.write(f"{item_name},{location},{can_be_picked}\n")

    def _save_locations(self, file):
        """Save all locations to the file."""
        file.write("[Locations]\n")
        for loc_name, data in self.locations.items():
            desc = data.get("description", "")
            connections = data.get("connections", {})
            connections_str = ";".join(
                [f"{dir}={loc}" for dir, loc in connections.items()]
            )
            file.write(f"{loc_name},{desc},{connections_str}\n")

    def _save_creatures(self, file):
        """Save all creatures to the file."""
        file.write("[Creatures]\n")
        for creature_name, data in self.creatures.items():
            desc = data.get("description", "")
            location = data.get("location", "None")
            is_pymon = data.get("is_pymon", False)
            file.write(f"{creature_name},{desc},{location},{is_pymon}\n")

    def _save_user_pymon(self, file):
        """Save the current user's Pymon to the file."""
        file.write("[UserPymon]\n")
        user_pymon = self.user_pymon
        file.write(
            f"{user_pymon.get('nickname', '')},{user_pymon.get('description', '')}\n"
        )
        file.write(f"{user_pymon.get('location', 'None')}\n")

        stats = user_pymon.get("stats", {})
        file.write(
            f"{stats.get('energy', 3)},{stats.get('has_immunity', False)},{stats.get('move_count', 0)}\n"
        )

        inventory = user_pymon.get("inventory", [])
        file.write(",".join(inventory) + "\n")

        self._save_battle_stats(file, stats.get("battle_stats", []))

    def _save_battle_stats(self, file, battle_stats):
        """Save the battle statistics of the user's Pymon."""
        for stat in battle_stats:
            stat_str = f"{stat['timestamp']},{stat['opponent']},{stat['wins']},{stat['draws']},{stat['losses']}"
            file.write(stat_str + "\n")

    def _save_bench_pymons(self, file):
        """Save the Pymons on the bench to the file."""
        file.write("[BenchPymons]\n")
        for pymon in self.bench_pymons:
            inventory_str = ",".join(item.name for item in pymon.get("inventory", []))
            file.write(f"{pymon['nickname']},{pymon['description']},{inventory_str}\n")

    def load_game(self, file_path="save2024.csv"):
        """
        Load a game state from a file.
        """
        try:
            if not os.path.exists(file_path):
                raise GameError(f"Save file not found: {file_path}")

            with open(file_path, "r") as file:
                section = None
                self.items = {}
                self.locations = {}
                self.creatures = {}
                self.bench_pymons = []
                battle_stats = []
                user_pymon_lines = []

                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    section = self.update_section(line, section)

                    if section == "items":
                        self.load_item(line)
                    elif section == "locations":
                        self.load_location(line)
                    elif section == "creatures":
                        self.load_creature(line)
                    elif section == "user_pymon":
                        user_pymon_lines.append(line)
                        if len(user_pymon_lines) >= 4:
                            self.load_user_pymon(user_pymon_lines, battle_stats, line)
                    elif section == "bench_pymons":
                        self.load_bench_pymon(line)

            print(f"Game loaded successfully from {file_path}")

        except Exception as e:
            raise GameError(f"Failed to load game: {str(e)}")

    def update_section(self, line, section):
        """Update the current section being processed based on the line content."""
        if line == "[Items]":
            return "items"
        elif line == "[Locations]":
            return "locations"
        elif line == "[Creatures]":
            return "creatures"
        elif line == "[UserPymon]":
            return "user_pymon"
        elif line == "[BenchPymons]":
            return "bench_pymons"
        return section

    def load_item(self, line):
        """Load an item from the save file."""
        name, location, can_be_picked = line.split(",")
        self.items[name] = {
            "location": location,
            "can_be_picked": can_be_picked.lower() == "true",
        }

    def load_location(self, line):
        """Load a location from the save file."""
        name, desc, connections = line.split(",", 2)
        connections_dict = {}
        if connections:
            for conn in connections.split(";"):
                if "=" in conn:
                    dir, loc = conn.split("=")
                    connections_dict[dir] = loc
        self.locations[name] = {
            "description": desc,
            "connections": connections_dict,
        }

    def load_creature(self, line):
        """Load a creature from the save file."""
        name, desc, location, is_pymon = line.split(",")
        self.creatures[name] = {
            "description": desc,
            "location": location,
            "is_pymon": is_pymon.lower() == "true",
        }

    def load_user_pymon(self, user_pymon_lines, battle_stats, line):
        """Load the user's Pymon and its stats from the save file."""
        if "," in line:  # This is a battle stat line
            timestamp, opponent, wins, draws, losses = line.split(",")
            battle_stats.append(
                {
                    "timestamp": timestamp,
                    "opponent": opponent,
                    "wins": int(wins),
                    "draws": int(draws),
                    "losses": int(losses),
                }
            )
        elif len(user_pymon_lines) == 4:  # Process basic data
            nickname, description = user_pymon_lines[0].split(",")
            location = user_pymon_lines[1]
            energy, has_immunity, move_count = user_pymon_lines[2].split(",")
            inventory = user_pymon_lines[3].split(",") if user_pymon_lines[3] else []

            self.user_pymon = {
                "nickname": nickname,
                "description": description,
                "location": location,
                "stats": {
                    "energy": int(energy),
                    "has_immunity": has_immunity.lower() == "true",
                    "move_count": int(move_count),
                    "battle_stats": battle_stats,
                },
                "inventory": inventory,
            }

    def load_bench_pymon(self, line):
        """Load a Pymon from the bench in the save file."""
        nickname, description, inventory = line.split(",", 2)
        inventory_items = inventory.split(",") if inventory else []
        self.bench_pymons.append(
            {
                "nickname": nickname,
                "description": description,
                "inventory": inventory_items,
            }
        )
