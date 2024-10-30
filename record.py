import random
import sys

from creature import Pymon, Animal
from exceptions import InvalidInputFileFormat
from item import Item
from location import Location
from game_state import GameState


class Record:
    def __init__(self):
        self._locations = []
        self._creatures = []
        self._game_state = GameState()

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

    def save_game_state(self, file_path='save2024.csv'):
        """Save the current game state."""
        try:
            # Update game state with current data
            for location in self._locations:
                self._game_state.locations[location.name] = {
                    'description': location.description,
                    'connections': {dir: loc.name for dir, loc in location.doors.items() if loc}
                }

            for creature in self._creatures:
                self._game_state.creatures[creature.nickname] = {
                    'description': creature.description,
                    'location': creature.location.name if creature.location else 'None',
                    'is_pymon': isinstance(creature, Pymon)
                }

            # Save the game state
            self._game_state.save_game(file_path)
            print(f"Game state saved to {file_path}")
        except Exception as e:
            print(f"Failed to save game state: {str(e)}")

    def load_game_state(self, file_path='save2024.csv'):
        """Load a saved game state."""
        try:
            # Load the game state
            self._game_state.load_game(file_path)

            # Reconstruct locations
            self._locations = []
            location_dict = {}
            
            # First pass: Create location objects
            for name, data in self._game_state.locations.items():
                location = Location(name, data['description'])
                self._locations.append(location)
                location_dict[name] = location

            # Second pass: Connect locations
            for name, data in self._game_state.locations.items():
                location = location_dict[name]
                for dir, connected_name in data['connections'].items():
                    if connected_name in location_dict:
                        location.doors[dir] = location_dict[connected_name]

            # Reconstruct creatures
            self._creatures = []
            for name, data in self._game_state.creatures.items():
                if data['is_pymon']:
                    creature = Pymon(name, data['description'])
                else:
                    creature = Animal(name, data['description'])
                
                if data['location'] != 'None' and data['location'] in location_dict:
                    creature.location = location_dict[data['location']]
                    creature.location.add_creature(creature)
                
                self._creatures.append(creature)

            print(f"Game state loaded from {file_path}")
        except Exception as e:
            print(f"Failed to load game state: {str(e)}")

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
            location_dict = {}  # Dictionary to map location names to Location objects
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, *doors = parts
                    location = Location(name.strip(), description.strip())
                    locations.append(location)
                    location_dict[name.strip()] = location  # Map name to Location object

            # Second pass to connect locations
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description, *doors = parts
                    location = location_dict[name.strip()]
                    for door in doors:
                        direction, connected_location_name = door.split("=")
                        connected_location = location_dict.get(
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
                creature.location = self._locations[location_index]
                creature.location.add_creature(creature)  # Add creature to the location

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
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    name, description = parts
                    can_be_picked = name.strip().lower() != "tree"  # Trees cannot be picked up
                    item = Item(name.strip(), description.strip(), can_be_picked)
                    location = random.choice(self._locations)
                    location.add_item(item)
                    # Update game state
                    self._game_state.items[item.name] = {
                        'location': location.name,
                        'can_be_picked': can_be_picked
                    }

        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading items: {e}")
