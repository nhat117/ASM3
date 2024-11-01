import sys
import random
import datetime
import csv


class Location:
    def __init__(self, name, description):
        self._name = name
        self._description = description
        self._doors = {"west": None, "north": None, "east": None, "south": None}
        self._creatures = []
        self._items = []

    @property
    def name(self):
        """Getter for name"""
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def description(self):
        """Getter for Description"""
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    @property
    def doors(self):
        """Getter for Doors"""
        return self._doors

    @doors.setter
    def doors(self, new_doors):
        if isinstance(new_doors, dict):
            self._doors = new_doors
        else:
            raise ValueError("Doors must be a dictionary")

    @property
    def creatures(self):
        """Getter for the creatures present in the location."""
        return self._creatures

    @creatures.setter
    def creatures(self, new_creatures):
        if isinstance(new_creatures, list):
            self._creatures = new_creatures
        else:
            raise ValueError("Creatures must be a list")

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, new_items):
        if isinstance(new_items, list):
            self.items = new_items
        else:
            raise ValueError("Items must be a list")

    def connect(self, direction, location):
        """Connect this location to another one in a given direction."""
        if direction in self.doors:
            self.doors[direction] = location
            # Connect the other location in the opposite direction
            if direction == "west":
                location.doors["east"] = self
            elif direction == "north":
                location.doors["south"] = self
            elif direction == "east":
                location.doors["west"] = self
            elif direction == "south":
                location.doors["north"] = self

    def add_creature(self, creature):
        """Add a creature to the location."""
        self._creatures.append(creature)

    def add_item(self, item):
        """Add an item to the location."""
        self._items.append(item)

    def inspect(self):
        """Inspect the location and display its details."""
        print(f"You are at {self._name}. {self._description}")
        if self._creatures:
            for creature in self._creatures:
                print(f"Creature present: {creature.nickname} - {creature.description}")
        else:
            print("No creatures here.")
        if self._items:
            for item in self._items:
                print(f"Item present: {item.name} - {item.description}")
        else:
            print("No items here.")

    def validate_new_location(self, new_name, new_doors, existing_locations):
        """Validate a new location against existing ones."""
        # Check for blank fields
        if not new_name:
            raise ValueError("Location name must be specified.")

        # Ensure at least one direction is not None
        if all(direction is None for direction in new_doors.values()):
            raise ValueError("At least one direction must be specified.")

        # Check for unique location name
        if new_name in [loc.name for loc in existing_locations]:
            raise ValueError("Location name must be unique.")

        # Check for similar locations
        for loc in existing_locations:
            if loc.doors == new_doors:
                raise ValueError("A similar location with the same connections already exists.")

        # Check if all specified directions exist
        for direction, location_name in new_doors.items():
            if location_name and location_name not in [loc.name for loc in existing_locations]:
                raise ValueError(f"Location in direction {direction} does not exist: {location_name}")

    def update_csv_with_new_location(self, new_location, csv_path='locations.csv'):
        """Update the CSV file with the new location and its connections."""
        # Read existing locations
        with open(csv_path, mode='r') as file:
            reader = csv.reader(file)
            locations = list(reader)

        # Update connections for existing locations
        updated_locations = []
        for loc in locations:
            loc_name, loc_desc, *loc_doors = loc
            loc_doors_dict = dict(zip(["west", "north", "east", "south"], loc_doors))
            for direction, connected_loc in loc_doors_dict.items():
                if connected_loc == new_location.name:
                    loc_doors_dict[direction] = new_location.name
                # Ensure bidirectional update
                if direction == "west" and loc_doors_dict["east"] == new_location.name:
                    loc_doors_dict["east"] = loc_name
                elif direction == "north" and loc_doors_dict["south"] == new_location.name:
                    loc_doors_dict["south"] = loc_name
                elif direction == "east" and loc_doors_dict["west"] == new_location.name:
                    loc_doors_dict["west"] = loc_name
                elif direction == "south" and loc_doors_dict["north"] == new_location.name:
                    loc_doors_dict["north"] = loc_name
            updated_locations.append([loc_name, loc_desc] + list(loc_doors_dict.values()))

        # Add the new location
        new_loc_entry = [new_location.name, new_location.description] + list(new_location.doors.values())
        updated_locations.append(new_loc_entry)

        # Write updated locations back to CSV
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_locations)
