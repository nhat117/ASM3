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
        print("\n##### Game World Setup #####\n")

        # Display Locations and their connections
        print("##### Locations #####")
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
        print("\n##### Items #####")
        for item_name, data in self.items.items():
            loc = data.get("location", "Unknown")
            is_pickable = data.get("is_pickable", True)
            print(f"\nItem: {item_name}")
            print(f"Location: {loc}")
            print(f"Can be picked: {is_pickable}")

        # Display Creatures and their locations
        print("\n#### Creatures #####")
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
                self._save_bench(file)

            print(f"Game saved successfully to {file_path}")

        except Exception as e:
            raise GameError(f"Failed to save game: {str(e)}")

    def _save_items(self, file):
        """Save all items to the file."""
        file.write("[Items]\n")
        for item_name, data in self.items.items():
            location = data.get("location", "None")
            is_pickable = data.get("is_pickable", True)
            file.write(f"{item_name},{location},{is_pickable}\n")

    def _save_locations(self, f):
        """Save all locations to the file."""
        f.write("[Locations]\n")
        for loc_name, data in self.locations.items():
            desc = data.get("description", "")
            connections = data.get("connections", {})
            connections_str = ";".join(
                [f"{dir}={loc}" for dir, loc in connections.items()]
            )
            f.write(f"{loc_name},{desc},{connections_str}\n")

    def _save_creatures(self, f):
        """Save all creatures to the file."""
        f.write("[Creatures]\n")
        for creature_name, data in self.creatures.items():
            desc = data.get("description", "")
            loc = data.get("location", "None")
            is_pymon = data.get("is_pymon", False)
            f.write(f"{creature_name},{desc},{loc},{is_pymon}\n")

    def _save_user_pymon(self, f):
        """Save the current user's Pymon to the file."""
        f.write("[UserPymon]\n")
        user_pymon = self.user_pymon
        f.write(
            f"{user_pymon.get('nickname', '')},{user_pymon.get('description', '')}\n"
        )
        f.write(f"{user_pymon.get('location', 'None')}\n")

        stats = user_pymon.get("stats", {})
        f.write(
            f"{stats.get('energy', 3)},{stats.get('has_immunity', False)},{stats.get('move_count', 0)}\n"
        )

        # Save inventory items by their names only
        inventory = [str(item) if isinstance(item, str) else item.name for item in user_pymon.get("inventory", [])]
        f.write(",".join(inventory) + "\n")

        self._save_stats_battle(f, stats.get("battle_stats", []))

    def _save_stats_battle(self, file, battle_stats):
        """Save the battle statistics of the user's Pymon."""
        for stat in battle_stats:
            stat_str = f"{stat['timestamp']},{stat['opponent']},{stat['wins']},{stat['draws']},{stat['losses']}"
            file.write(stat_str + "\n")

    def _save_bench(self, f):
        """Save the Pymons on the bench to the file."""
        f.write("[BenchPymons]\n")
        for pymon in self.bench_pymons:
            # Save inventory items by their names only
            inventory = [str(item) if isinstance(item, str) else item.name for item in pymon.get("inventory", [])]
            inventory_str = ",".join(inventory)
            f.write(f"{pymon['nickname']},{pymon['description']},{inventory_str}\n")

    def load_game(self, file_path="save2024.csv"):
        """
        Load a game state from a file.
        """
        try:
            if not os.path.exists(file_path):
                raise GameError(f"Save file not found: {file_path}")

            with open(file_path, "r") as f:
                section = None
                self.items = {}
                self.locations = {}
                self.creatures = {}
                self.bench_pymons = []
                battle_stats = []
                user_pymon_lines = []

                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("["):
                        section = line.lower().strip("[]")
                        continue

                    if section == "items":
                        self.load_item_data(line)
                    elif section == "locations":
                        self.load_loc(line)
                    elif section == "creatures":
                        self.load_creature(line)
                    elif section == "userpymon":
                        user_pymon_lines.append(line)
                        if len(user_pymon_lines) == 4:  # We have all the basic user Pymon data
                            self.load_user_pymon(user_pymon_lines)
                        elif len(user_pymon_lines) > 4:  # These are battle stats
                            self.load_battle_stats(line, battle_stats)
                    elif section == "benchpymons":
                        self.load_bench(line)

            print(f"Game loaded successfully from {file_path}")

        except Exception as e:
            raise GameError(f"Failed to load game: {str(e)}")

    def load_item_data(self, line):
        """Load an item from the save file."""
        if "," not in line:
            return
        parts = line.split(",")
        if len(parts) < 3:
            return
        name, location, is_pickable = parts
        self.items[name] = {
            "location": location,
            "is_pickable": is_pickable.lower() == "true",
        }

    def load_loc(self, line):
        """Load a location from the save file."""
        if "," not in line:
            return
        parts = line.split(",", 2)
        if len(parts) < 3:
            return
        name, desc, connections = parts
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
        if "," not in line:
            return
        parts = line.split(",")
        if len(parts) < 4:
            return
        name, desc, loc, is_pymon = parts
        self.creatures[name] = {
            "description": desc,
            "location": loc,
            "is_pymon": is_pymon.lower() == "true",
        }

    def load_user_pymon(self, lines):
        """Load the user's Pymon data from the save file."""
        if len(lines) < 4:
            return

        # First line contains nickname and description
        nickname_desc = lines[0].split(",", 1)
        if len(nickname_desc) < 2:
            return
        nickname, desc = nickname_desc

        # Second line contains location
        location = lines[1]

        # Third line contains stats
        stats_parts = lines[2].split(",")
        if len(stats_parts) < 3:
            return
        energy, has_immunity, move_count = stats_parts

        # Fourth line contains inventory
        inventory = lines[3].split(",") if lines[3] else []

        self.user_pymon = {
            "nickname": nickname,
            "description": desc,
            "location": location,
            "stats": {
                "energy": int(energy),
                "has_immunity": has_immunity.lower() == "true",
                "move_count": int(move_count),
                "battle_stats": [],
            },
            "inventory": inventory,
        }

    def load_battle_stats(self, line, battle_stats):
        """Load battle statistics for the user's Pymon."""
        parts = line.split(",")
        if len(parts) == 5:
            timestamp, opponent, wins, draws, losses = parts
            battle_stats.append({
                "timestamp": timestamp,
                "opponent": opponent,
                "wins": int(wins),
                "draws": int(draws),
                "losses": int(losses),
            })
            self.user_pymon["stats"]["battle_stats"] = battle_stats

    def load_bench(self, line):
        """Load a Pymon from the bench in the save file."""
        if "," not in line:
            return
        parts = line.split(",", 2)
        if len(parts) < 3:
            return
        nickname, desc, inventory = parts
        inventory_items = inventory.split(",") if inventory else []
        self.bench_pymons.append({
            "nickname": nickname,
            "description": desc,
            "inventory": inventory_items,
        })
