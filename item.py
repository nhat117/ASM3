# Item class
import sys
import random
import datetime

class Item:
    def __init__(self, name, description, can_be_picked=True, effect=None):
        self._name = name
        self._description = description
        self._can_be_picked = can_be_picked  # Some items can't be picked (e.g., trees)
        self._effect = (
            effect  # Effect of the item (e.g., "restore_energy", "grant_immunity")
        )

    # Getter and setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    # Getter and setter for description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    # Getter and setter for can_be_picked
    @property
    def can_be_picked(self):
        return self._can_be_picked

    @can_be_picked.setter
    def can_be_picked(self, new_can_be_picked):
        if isinstance(new_can_be_picked, bool):
            self._can_be_picked = new_can_be_picked
        else:
            raise ValueError("can_be_picked must be a boolean value.")

    # Getter and setter for effect
    @property
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, new_effect):
        self._effect = new_effect

    def apply(self, pymon):
        """Apply the effect of the item to the Pymon."""
        if self._effect == "restore_energy":
            pymon.energy = min(3, pymon.energy + 1)
            print(f"{pymon.nickname}'s energy is restored! Energy: {pymon.energy}/3")
        elif self._effect == "grant_immunity":
            pymon.has_immunity = True
            print(f"{pymon.nickname} is now immune for one battle!")
