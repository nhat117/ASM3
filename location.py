import sys
import random
import datetime


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
