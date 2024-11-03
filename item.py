""""
Assignment: Pymon Game Assignment 3
Course: COSC2531 - Programming Fundamentals
Author: Thomas Bui
Student ID: s3878174
Highest Part Attempted: HD
"""

MAX_ENERGY = 3
ENERGY_PLUS_RATE = 1


class Item:
    def __init__(self, name, desc, is_pickable=True, is_consumable=False, effect=None):
        """Initialize the Item object."""
        self.__name = name
        self.__desc = desc
        self.__is_pickable = is_pickable
        self.__is_consumable = is_consumable
        self.__effect = effect

    @property
    def name(self):
        """Getter for name"""
        return self.__name

    @name.setter
    def name(self, new_name):
        """Setter for name"""
        self.__name = new_name

    @property
    def desc(self):
        """Getter for Description"""
        return self.__desc

    @desc.setter
    def desc(self, desc):
        """Setter for Description"""
        self.__desc = desc

    @property
    def is_pickable(self):
        """Getter for is_pickable"""
        return self.__is_pickable

    @is_pickable.setter
    def is_pickable(self, is_pickable):
        """Setter for can_be_picked"""
        if isinstance(is_pickable, bool):
            self.__is_pickable = is_pickable
        else:
            raise ValueError("must be a boolean value.")

    @property
    def is_consumable(self):
        """Getter for is_consumable"""
        return self.__is_consumable

    @is_consumable.setter
    def is_consumable(self, is_consumable):
        """Setter for is_consumable"""
        if isinstance(is_consumable, bool):
            self.__is_consumable = is_consumable
        else:
            raise ValueError("must be a boolean value.")

    @property
    def effect(self):
        """Getter for effect"""
        return self.__effect

    @effect.setter
    def effect(self, new_effect):
        """Setter for effect"""
        self.__effect = new_effect
