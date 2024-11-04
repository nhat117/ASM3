from game_state import GameState
from location import Location
from creature import Pymon, Animal
from exceptions import GameError
from direction import Direction


class Record:
    def __init__(self):
        """Initialize Record with empty lists for locations and creatures."""
        self.locations = []
        self.creatures = []
        self.game_state = GameState()

    def load_data(self, locations_file="locations.csv", creatures_file="creatures.csv", items_file="items.csv"):
        """Load all game data from specified files."""
        try:
            self.load_locations(locations_file)
            self.load_creatures(creatures_file)
            # Note: items loading would be handled by the Location class when loading locations
        except GameError as e:
            raise GameError(f"Error loading data: {str(e)}")

    def load_locations(self, file_path):
        """Load locations from a CSV file."""
        try:
            with open(file_path, "r") as f:
                # Skip header line
                header = f.readline()

                for line in f:
                    # Split the line and strip whitespace from each part
                    parts = [part.strip() for part in line.split(",")]

                    if len(parts) >= 6:
                        name = parts[0]
                        desc = parts[1]
                        west = parts[2]
                        north = parts[3]
                        east = parts[4]
                        south = parts[5]

                        # Create location with name and description
                        location = Location(name, desc)

                        # Create Direction object and set connections
                        doors = Direction()
                        doors.west = west if west != "None" else None
                        doors.north = north if north != "None" else None
                        doors.east = east if east != "None" else None
                        doors.south = south if south != "None" else None
                        location.doors = doors

                        self.locations.append(location)

            # Set up bi-directional connections
            for loc in self.locations:
                doors_dict = loc.doors.to_dict()
                for direction, connected_name in doors_dict.items():
                    if connected_name != 'None' and connected_name is not None:
                        connected_location = self.find_location(connected_name)
                        if connected_location:
                            # Use property setter directly
                            loc.doors.set_direction(connected_location, direction)

        except FileNotFoundError:
            raise GameError(f"Location file not found: {file_path}")
        except Exception as e:
            raise GameError(f"Error loading locations: {str(e)}")

    def find_location(self, name):
        """Find a location by name."""
        for loc in self.locations:
            if loc.name == name:
                return loc
        return None

    def find_item_in_locations(self, item_name):
        """Find an item by name across all locations and return the item and its location."""
        item_res, location_res = None, None
        for location in self.locations:  # Loop through locaiton
            for item in location.items:  # Loop through item
                if item.name == item_name:  # If match location
                    item_res = item
                    location_res = location
                    break
        return item_res, location_res

    def transfer_item(self, item, from_location, to_pymon):
        """Transfer an item from a location to a Pymon's inventory."""
        if item in from_location.items:
            from_location.items.remove(item)
            to_pymon.inventory.append(item)
            return True
        return False

    def set_inventory(self, new_pymon, selected_pymon):
        """Set the inventory for the new Pymon."""
        if selected_pymon.get("inventory"):
            for item_name in selected_pymon["inventory"]:
                item, location = self.find_item_in_locations(item_name)
                if item and location:
                    self.transfer_item(item, location, new_pymon)

    def load_creatures(self, file_path):
        """Load creatures from a CSV file."""
        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = []
                    for part in line.split(","):
                        parts.append(part.strip())

                    if len(parts) >= 3:
                        nickname = parts[0]
                        desc = parts[1]
                        is_pymon = parts[2].lower() == "yes"

                        # Create appropriate creature type
                        creature = (
                            Pymon(nickname, desc)
                            if is_pymon
                            else Animal(nickname, desc)
                        )
                        self.creatures.append(creature)

        except FileNotFoundError:
            raise GameError(f"Creatures file not found: {file_path}")
        except Exception as e:
            raise GameError(f"Error loading creatures: {str(e)}")

    def save_game_state(self, file_path, pymon):
        """Save the current game state."""
        try:
            # Update game state with current data
            self.game_state.user_pymon = {
                "nickname": pymon.nickname,
                "description": pymon.desc,
                "location": pymon.loc.name if pymon.loc else "None",
                "stats": {
                    "energy": pymon.energy,
                    "has_immunity": pymon.has_immunity,
                    "move_count": pymon.move_count,
                    "battle_stats": pymon.battle_stats,
                },
                "inventory": [item.name for item in pymon.inventory],
            }

            # Save game state
            self.game_state.save_game(file_path)

        except Exception as e:
            raise GameError(f"Failed to save game state: {str(e)}")

    def add_creature(self, creature):
        """Add creature to record"""
        self.creatures.append(creature)

    def add_location(self, loc):
        self.locations.append(loc)

    def set_pymon_location(self, pymon, loc_name):
        """Set the location of a Pymon based on location name."""
        if loc_name != "None":
            for loc in self.locations:  # Loop through the locations
                if loc.name == loc_name:
                    pymon.loc = loc
                    break

    def load_game_state(self, f_path):
        """Load a saved game state."""
        try:
            # Load game state
            self.game_state.load_game(f_path)

            # Create Pymon from loaded data
            user_pymon_data = self.game_state.user_pymon
            if user_pymon_data:
                # Create Pymon instance
                pymon = Pymon(
                    user_pymon_data["nickname"],
                    user_pymon_data["description"],
                )

                # Set location using the helper method
                loc_name = user_pymon_data["location"]
                self.set_pymon_location(pymon, loc_name)

                # Set stats
                stats = user_pymon_data["stats"]
                pymon.energy = stats["energy"]
                pymon.has_immunity = stats["has_immunity"]
                pymon.move_count = stats["move_count"]
                pymon.battle_stats = stats["battle_stats"]

                # Set inventory using the abstracted method
                self.set_inventory(pymon, user_pymon_data)

                return pymon

        except Exception as e:
            raise GameError(f"Failed to load game state: {str(e)}")

        return None
