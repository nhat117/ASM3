import random
import sys
from creature import Pymon, Animal
from exceptions import InvalidInputFileFormat
from item import Item
from location import Location
from game_state import GameState


class Record:
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one Record instance."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        """Initialize the Record with locations, creatures, and game state."""
        if not hasattr(self, "__initialized"):  # To prevent reinitialization
            self.__locations = []
            self.__creatures = []
            self.__game_state = GameState()
            self.__current_pymon = None
            self.__initialized = True  # Mark as initialized to avoid reinitialization

    # Additional methods for the Record class can be added here

    # Getter and setter for locations
    @property
    def locations(self):
        return self.__locations

    @locations.setter
    def locations(self, new_locations):
        if isinstance(new_locations, list):
            self.__locations = new_locations
        else:
            raise ValueError("Locations must be a list.")

    # Getter and setter for creatures
    @property
    def creatures(self):
        return self.__creatures

    @creatures.setter
    def creatures(self, new_creatures):
        if isinstance(new_creatures, list):
            self.__creatures = new_creatures
        else:
            raise ValueError("Creatures must be a list.")

    # Getter and setter for current_pymon
    @property
    def current_pymon(self):
        return self.__current_pymon

    @current_pymon.setter
    def current_pymon(self, new_pymon):
        if isinstance(new_pymon, Pymon):
            self.__current_pymon = new_pymon
        else:
            raise ValueError("Current Pymon must be a Pymon object.")

    # Game state getter
    @property
    def game_state(self):
        return self.__game_state

    # Game state setter
    @game_state.setter
    def game_state(self, new_game_state):
        if isinstance(new_game_state, GameState):
            self.__game_state = new_game_state
        else:
            raise ValueError("Game state must be a GameState object.")

    def save_game_state(self, file_path="save2024.csv", current_pymon=None):
        """Save the current game state."""
        try:
            # Store current Pymon
            if current_pymon is not None:
                self.__current_pymon = current_pymon
                # Update game state with current Pymon data
                if current_pymon.loc is not None:
                    location = current_pymon.loc.name
                else:
                    location = "None"

                inventory = []
                for item in current_pymon.inventory:
                    inventory.append(item.name)

                self.__game_state.user_pymon = {
                    "nickname": current_pymon.nickname,
                    "description": current_pymon.desc,
                    "location": location,
                    "stats": {
                        "energy": current_pymon.energy,
                        "has_immunity": current_pymon.has_immunity,
                        "move_count": current_pymon.move_count,
                        "battle_stats": current_pymon.battle_stats,
                    },
                    "inventory": inventory,
                }

            # Update game state with current data
            # Update game state with current data
            for location in self.__locations:
                location_data = {
                    "description": location.desc,
                    "connections": {}
                }
                for dir, loc in location.doors.items():
                    if loc:
                        location_data["connections"][dir] = loc.name
                self.__game_state.locations[location.name] = location_data

            for creature in self.__creatures:
                self.__game_state.creatures[creature.nickname] = {
                    "description": creature.desc,
                    "location": creature.loc.name if creature.loc else "None",
                    "is_pymon": isinstance(creature, Pymon),
                }

            # Save the game state
            self.__game_state.save_game(file_path)
            print(f"Game state saved to {file_path}")
        except Exception as e:
            print(f"Failed to save game state: {str(e)}")

    def load_game_state(self, file_path="save2024.csv"):
        """Load a saved game state."""
        try:
            # Load the game state
            self.__game_state.load_game(file_path)

            # Reconstruct game components
            location_dict = self._reconstruct_locations()
            self.__creatures = self._creatures_reader(location_dict)
            self.__current_pymon = self._user_pymon_reader(location_dict)
            self._bench_pymons_reader()

            print(f"Game state loaded from {file_path}")
            return self.__current_pymon
        except Exception as e:
            print(f"Failed to load game state: {str(e)}")
            return None

    def _reconstruct_locations(self):
        """Reconstruct all locations from the saved game state."""
        self.__locations = []
        location_dict = {}

        # First pass: Create location objects
        for name, data in self.__game_state.locations.items():
            location = Location(name, data["description"])
            self.__locations.append(location)
            location_dict[name] = location

        # Second pass: Connect locations
        for name, data in self.__game_state.locations.items():
            location = location_dict[name]
            for dir, connected_name in data["connections"].items():
                if connected_name in location_dict:
                    location.doors[dir] = location_dict[connected_name]

        return location_dict

    def _creatures_reader(self, location_dict):
        """Reconstruct all creatures from the saved game state."""
        creatures = []
        for name, data in self.__game_state.creatures.items():
            creature = (
                Pymon(name, data["description"])
                if data["is_pymon"]
                else Animal(name, data["description"])
            )

            if data["location"] != "None" and data["location"] in location_dict:
                creature.loc = location_dict[data["location"]]
                creature.loc.add_creature(creature)

            creatures.append(creature)

        return creatures

    def _user_pymon_reader(self, location_dict):
        """Reconstruct the current user's Pymon if it exists in the saved game state."""
        user_data = self.__game_state.user_pymon
        if user_data and isinstance(user_data, dict):
            current_pymon = Pymon(user_data["nickname"], user_data["description"])

            # Set location
            if user_data["location"] != "None":
                if user_data["location"] in location_dict:
                    current_pymon.loc = location_dict[user_data["location"]]

            # Set stats
            stats = user_data.get("stats", {})
            current_pymon.energy = stats.get("energy", 3)
            current_pymon.has_immunity = stats.get("has_immunity", False)
            current_pymon.move_count = stats.get("move_count", 0)
            current_pymon.battle_stats = stats.get("battle_stats", [])

            # Set inventory
            if "inventory" in user_data:
                self._set_pymon_inventory(current_pymon, user_data["inventory"])

            return current_pymon
        return None

    def _set_pymon_inventory(self, pymon, inventory):
        """Assign inventory items to a Pymon."""
        for item_name in inventory:
            # Find the item in locations
            for location in self.__locations:
                item = location.get_item(item_name)
                if item:
                    pymon.inventory.append(item)
                    location.items.remove(item)
                    break

    def _bench_pymons_reader(self):
        """Reconstruct bench Pymons from the saved game state."""
        bench_pymons = []
        for pymon_data in self.__game_state.bench_pymons:
            bench_pymon = {
                "nickname": pymon_data["nickname"],
                "description": pymon_data["description"],
                "inventory": pymon_data["inventory"],
            }
            bench_pymons.append(bench_pymon)
        self.__game_state.bench_pymons = bench_pymons

    def load_data(
            self,
            locations_file="locations.csv",
            creatures_file="creatures.csv",
            items_file="items.csv",
    ):
        try:
            self.__locations = self._load_loc_list(locations_file)
            self.__creatures = self._load_creatures(creatures_file)
            self._load_items(items_file)
        except InvalidInputFileFormat as e:
            print(e)
            sys.exit(0)

    def _load_loc_list(self, f_name):
        try:
            locations = []
            location_tmp = {}  # Dictionary to map location names to Location objects
            with open(f_name, "r") as f:
                next(f)  # Skip header line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, west, north, east, south = parts
                    loc = Location(name.strip(), description.strip())
                    locations.append(loc)
                    location_tmp[name.strip()] = loc

            # Second pass to connect locations
            with open(f_name, "r") as f:
                next(f)  # Skip header line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, west, north, east, south = parts
                    loc = location_tmp[name.strip()]

                    # Set connections based on directions
                    directions = {
                        'west': west.strip(),
                        'north': north.strip(),
                        'east': east.strip(),
                        'south': south.strip()
                    }

                    for direction, connected_name in directions.items():
                        if connected_name != 'None':
                            connected_location = location_tmp.get(connected_name)
                            if connected_location:
                                loc.doors[direction] = connected_location

            return locations
        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading locations: {e}")

    def _load_creatures(self, f_name):
        try:
            creatures = []
            with open(f_name, "r") as f:
                next(f)  # Skip header line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    nickname, description, adoptable = parts
                    if adoptable.strip().lower() == "yes":
                        creature = Pymon(nickname.strip(), description.strip())
                    else:
                        creature = Animal(nickname.strip(), description.strip())
                    creatures.append(creature)

            # Randomly assign creatures to locations
            location_count = len(self.locations)
            for i, creature in enumerate(creatures):
                location_index = i % location_count
                creature.loc = self.locations[location_index]
                creature.loc.add_creature(creature)  # Add creature to the location

            return creatures
        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading creatures: {e}")

    def _load_items(self, f_name):
        try:
            with open(f_name, "r") as f:
                next(f)  # Skip header line
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = [part.strip() for part in line.split(",")]
                    name, desc, pickable, consumable = parts

                    # Convert string values to boolean
                    is_pickable = pickable.lower() == "yes"
                    is_consumable = consumable.lower() == "yes"

                    item = Item(name, desc, is_pickable, is_consumable)
                    loc = random.choice(self.locations)  # Randomly assign items to locations
                    loc.add_item(item)
                    # Update game state
                    self.game_state.items[item.name] = {
                        "location": loc.name,
                        "is_pickable": is_pickable,
                        "is_consumable": is_consumable
                    }

        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading items: {e}")
