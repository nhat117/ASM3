import os
from exceptions import GameError
from direction import Direction


class GameState:
    __instance = None
    MAX_ENERGY = 3  # Maximum energy level for Pymons

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one GameState instance."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

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

    def __parse_line(self, line):
        """Helper method to parse CSV lines into parts."""
        parts = []
        for p in line.split(","):
            parts.append(p.strip())
        return parts

    def __parse_inventory(self, inventory_str):
        """Helper method to parse inventory string into a list of items."""
        if not inventory_str:
            return []

        inventory_items = []
        for item in inventory_str.split(","):
            inventory_items.append(item.strip())

        return inventory_items

    def save_game(self, file_path="save2024.csv"):
        """
        Save the current game state to a file in the following format:
        [Items], [Locations], [Creatures], [UserPymon], [BenchPymons].
        """
        try:
            with open(file_path, "w") as f:
                self.__save_items(f)
                self.__save_locations(f)
                self.__save_creatures(f)
                self.__save_user_pymon(f)
                self.__save_bench(f)

            print(f"Game saved successfully to {file_path}")

        except Exception as e:
            raise GameError(f"Failed to save game: {str(e)}")

    def __save_items(self, f):
        """Save all items to the file."""
        f.write("[Items]\n")
        for item_name, data in self.items.items():
            location = data.get("location", "None")
            is_pickable = data.get("is_pickable", True)
            is_consumable = data.get("is_consumable", False)
            f.write(f"{item_name}, {location}, {is_pickable}, {is_consumable}\n")

    def __save_locations(self, f):
        """Save all locations to the file."""
        f.write("[Locations]\n")
        for loc_name, data in self.locations.items():
            desc = data.get("description", "")
            doors = data.get("connections", Direction())

            # Convert Direction object to dictionary if needed
            if isinstance(doors, Direction):
                connections = doors.to_dict()
            else:
                connections = doors

            # Create a list of direction-location pairs in the correct format
            connections_list = []
            for direction in ["west", "north", "east", "south"]:
                location = connections.get(direction, "None")
                connections_list.append(f"{direction} = {location}")

            # Join all parts with the correct delimiter format
            line = f"{loc_name}, {desc}, {', '.join(connections_list)}\n"
            f.write(line)

    def __save_creatures(self, f):
        """Save all creatures to the file."""
        f.write("[Creatures]\n")
        for creature_name, data in self.creatures.items():
            desc = data.get("description", "")
            loc = data.get("location", "None")
            is_pymon = data.get("is_pymon", False)
            f.write(f"{creature_name}, {desc}, {loc}, {is_pymon}\n")

    def __save_user_pymon(self, f):
        """Save the current user's Pymon to the file."""
        f.write("[UserPymon]\n")
        user_pymon = self.user_pymon
        f.write(
            f"{user_pymon.get('nickname', '')}, {user_pymon.get('description', '')}\n"
        )
        f.write(f"{user_pymon.get('location', 'None')}\n")

        stats = user_pymon.get("stats", {})
        f.write(
            f"{stats.get('energy', 3)}, {stats.get('has_immunity', False)}, {stats.get('move_count', 0)}\n"
        )

        # Save inventory items by their names only
        inventory = []
        for item in user_pymon.get("inventory", []):
            if isinstance(item, str):
                inventory.append(str(item))
            else:
                inventory.append(item.name)
        f.write(", ".join(inventory) + "\n")

        self.__save_stats_battle(f, stats.get("battle_stats", []))

    def __save_stats_battle(self, f, battle_stats):
        """Save the battle statistics of the user's Pymon."""
        for stat in battle_stats:
            stat_str = f"{stat['timestamp']}, {stat['opponent']}, {stat['wins']}, {stat['draws']}, {stat['losses']}"
            f.write(stat_str + "\n")

    def __save_bench(self, f):
        """Save the Pymons on the bench to the file."""
        f.write("[BenchPymons]\n")
        for pymon in self.bench_pymons:
            # Save inventory items by their names only
            inventory = []
            for item in pymon.get("inventory", []):
                if isinstance(item, str):
                    inventory.append(str(item))
                else:
                    inventory.append(item.name)
            inventory_str = ", ".join(inventory)
            f.write(f"{pymon['nickname']}, {pymon['description']}, {inventory_str}\n")

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
        parts = self.__parse_line(line)
        if len(parts) < 4:
            return
        name, location, is_pickable, is_consumable = parts
        self.items[name] = {
            "location": location,
            "is_pickable": is_pickable.lower() == "true",
            "is_consumable": is_consumable.lower() == "true"
        }

    def load_loc(self, line):
        """Load a location from the save file."""
        if "," not in line:
            return
        parts = self.__parse_line(line)
        if len(parts) < 3:
            return
        name = parts[0]
        desc = parts[1]

        # Create a new Direction object
        doors = Direction()

        # Process connections
        for conn in parts[2:]:
            if "=" in conn:
                split_conn = conn.split("=")
                direction = split_conn[0].strip()
                loc = split_conn[1].strip()

                if loc.lower() != "none":
                    doors.set_direction(loc, direction)
        self.locations[name] = {
            "description": desc,
            "connections": doors,
        }

    def load_creature(self, line):
        """Load a creature from the save file."""
        if "," not in line:
            return
        parts = self.__parse_line(line)
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
        parts = self.__parse_line(lines[0])
        if len(parts) < 2:
            return
        nickname, desc = parts

        # Second line contains location
        location = lines[1].strip()

        # Third line contains stats
        stats_parts = self.__parse_line(lines[2])
        if len(stats_parts) < 3:
            return
        energy, has_immunity, move_count = stats_parts

        # Fourth line contains inventory
        inventory = self.__parse_inventory(lines[3])

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
        parts = self.__parse_line(line)
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
        parts = self.__parse_line(line)
        bench_part_length = 3
        if len(parts) < bench_part_length:
            return
        nickname, desc, inventory = parts
        inventory_items = self.__parse_inventory(inventory)
        self.bench_pymons.append({
            "nickname": nickname,
            "description": desc,
            "inventory": inventory_items,
        })
