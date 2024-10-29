import random
import sys

from creature import Pymon, Animal
from exceptions import InvalidInputFileFormat
from item import Item
from location import Location


class Record:
    def __init__(self):
        self._locations = []
        self._creatures = []

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
                    item = Item(name.strip(), description.strip())
                    random.choice(self._locations).add_item(item)


        except Exception as e:
            raise InvalidInputFileFormat(f"Error loading items: {e}")
