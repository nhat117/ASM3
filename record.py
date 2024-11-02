import random
import sys
from creature import Pymon, Animal
from exceptions import InvalidInputFileFormat
from item import Item
from location import Location
from game_state import GameState


class Record:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one Record instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Record with locations, creatures, and game state."""
        if not hasattr(self, "_initialized"):  # To prevent reinitialization
            self._locations = []
            self._creatures = []
            self._game_state = GameState()
            self._current_pymon = None
            self._initialized = True  # Mark as initialized to avoid reinitialization

    # Additional methods for the Record class can be added here

    # Getter and setter for locations
    @property
    def locations(self):
        return self._locations

    @locations.setter
    def locations(self, new_locations):
        if isinstance(new_locations, list):
            self._locations = new_locations
        else:
            raise ValueError("Locations must be a list.")

    # Getter and setter for creatures
    @property
    def creatures(self):
        return self._creatures

    @creatures.setter
    def creatures(self, new_creatures):
        if isinstance(new_creatures, list):
            self._creatures = new_creatures
        else:
            raise ValueError("Creatures must be a list.")

    def save_game_state(self, file_path="save2024.csv", current_pymon=None):
        """Save the current game state."""
        try:
            # Store current Pymon
            if current_pymon:
                self._current_pymon = current_pymon
                # Update game state with current Pymon data
                self._game_state.user_pymon = {
                    "nickname": current_pymon.nickname,
                    "description": current_pymon.desc,
                    "location": (
                        current_pymon.loc.name
                        if current_pymon.loc
                        else "None"
                    ),
                    "stats": {
                        "energy": current_pymon.energy,
                        "has_immunity": current_pymon.has_immunity,
                        "move_count": current_pymon.move_count,
                        "battle_stats": current_pymon.battle_stats,
                    },
                    "inventory": [item.name for item in current_pymon.inventory],
                }

            # Update game state with current data
            for location in self._locations:
                self._game_state.locations[location.name] = {
                    "description": location.desc,
                    "connections": {
                        dir: loc.name for dir, loc in location.doors.items() if loc
                    },
                }

            for creature in self._creatures:
                self._game_state.creatures[creature.nickname] = {
                    "description": creature.desc,
                    "location": creature.loc.name if creature.loc else "None",
                    "is_pymon": isinstance(creature, Pymon),
                }

            # Save the game state
            self._game_state.save_game(file_path)
            print(f"Game state saved to {file_path}")
        except Exception as e:
            print(f"Failed to save game state: {str(e)}")

    def load_game_state(self, file_path="save2024.csv"):
        """Load a saved game state."""
        try:
            # Load the game state
            self._game_state.load_game(file_path)

            # Reconstruct game components
            location_dict = self._reconstruct_locations()
            self._creatures = self._creatures_reader(location_dict)
            self._current_pymon = self._user_pymon_reader(location_dict)
            self._bench_pymons_reader()

            print(f"Game state loaded from {file_path}")
            return self._current_pymon
        except Exception as e:
            print(f"Failed to load game state: {str(e)}")
            return None

    def _reconstruct_locations(self):
        """Reconstruct all locations from the saved game state."""
        self._locations = []
        location_dict = {}

        # First pass: Create location objects
        for name, data in self._game_state.locations.items():
            location = Location(name, data["description"])
            self._locations.append(location)
            location_dict[name] = location

        # Second pass: Connect locations
        for name, data in self._game_state.locations.items():
            location = location_dict[name]
            for dir, connected_name in data["connections"].items():
                if connected_name in location_dict:
                    location.doors[dir] = location_dict[connected_name]

        return location_dict

    def _creatures_reader(self, location_dict):
        """Reconstruct all creatures from the saved game state."""
        creatures = []
        for name, data in self._game_state.creatures.items():
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
        user_data = self._game_state.user_pymon
        if user_data and isinstance(user_data, dict):
            current_pymon = Pymon(user_data["nickname"], user_data["description"])

            # Set location
            if (
                    user_data["location"] != "None"
                    and user_data["location"] in location_dict
            ):
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
            for location in self._locations:
                item = next((i for i in location.items if i.name == item_name), None)
                if item:
                    pymon.inventory.append(item)
                    location.items.remove(item)
                    break

    def _bench_pymons_reader(self):
        """Reconstruct bench Pymons from the saved game state."""
        bench_pymons = []
        for pymon_data in self._game_state.bench_pymons:
            bench_pymon = {
                "nickname": pymon_data["nickname"],
                "description": pymon_data["description"],
                "inventory": pymon_data["inventory"],
            }
            bench_pymons.append(bench_pymon)
        self._game_state.bench_pymons = bench_pymons

    def load_data(
            self,
            locations_file="locations.csv",
            creatures_file="creatures.csv",
            items_file="items.csv",
    ):
        try:
            self._locations = self._load_locations(locations_file)
            self._creatures = self._load_creatures(creatures_file)
            self._load_items(items_file)
        except InvalidInputFileFormat as e:
            print(e)
            sys.exit(0)

    def _load_locations(self, filename):
        try:
            locations = []
            location_tmp = {}  # Dictionary to map location names to Location objects
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, *doors = parts
                    location = Location(name.strip(), description.strip())
                    locations.append(location)
                    location_tmp[name.strip()] = (
                        location  # Map name to Location object
                    )

            # Second pass to connect locations
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, *doors = parts
                    location = location_tmp[name.strip()]
                    for door in doors:
                        direction, connected_location_name = door.split("=")
                        connected_location = location_tmp.get(
                            connected_location_name.strip()
                        )
                        if connected_location:
                            location.doors[direction.strip()] = connected_location

            return locations
        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading locations: {e}")

    def _load_creatures(self, filename):
        try:
            creatures = []
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    nickname, description, adoptable = parts
                    creature = (
                        Pymon(nickname.strip(), description.strip())
                        if adoptable.strip().lower() == "yes"
                        else Animal(nickname.strip(), description.strip())
                    )
                    creatures.append(creature)

            # Randomly assign creatures to locations
            location_count = len(self._locations)
            for i, creature in enumerate(creatures):
                location_index = i % location_count
                creature.loc = self._locations[location_index]
                creature.loc.add_creature(creature)  # Add creature to the location

            # Debug: Print creatures assigned to each location
            for location in self._locations:
                print(f"Location: {location.name}")
                for creature in location.creatures:
                    print(f"- {creature.nickname}")
            return creatures
        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading creatures: {e}")

    def _load_items(self, filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description = parts
                    is_pickable = (
                            name.strip().lower() != "tree"
                    )  # Trees cannot be picked up
                    item = Item(name.strip(), description.strip(), is_pickable)
                    location = random.choice(self._locations)
                    location.add_item(item)
                    # Update game state
                    self._game_state.items[item.name] = {
                        "location": location.name,
                        "is_pickable": is_pickable,
                    }

        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading items: {e}")
