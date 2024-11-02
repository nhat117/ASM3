MAX_ENERGY = 3
ENERGY_PLUS_RATE = 1


class Item:
    def __init__(self, name, desc, is_pickable=True, effect=None):
        """Initialize the Item object."""
        self._name = name
        self._desc = desc
        self._is_pickable = is_pickable
        self._effect = (
            effect
        )

    @property
    def name(self):
        """Getter for name"""
        return self._name

    @name.setter
    def name(self, new_name):
        """Setter for name"""
        self._name = new_name

    @property
    def desc(self):
        """Getter for Description"""
        return self._desc

    @desc.setter
    def desc(self, desc):
        """Setter for Description"""
        self._desc = desc

    @property
    def is_pickable(self):
        """Getter for is_pickable"""
        return self._is_pickable

    @is_pickable.setter
    def is_pickable(self, is_pickable):
        """Setter for can_be_picked"""
        if isinstance(is_pickable, bool):
            self._is_pickable = is_pickable
        else:
            raise ValueError("must be a boolean value.")

    @property
    def effect(self):
        """Getter for effect"""
        return self._effect

    @effect.setter
    def effect(self, new_effect):
        """Setter for effect"""
        self._effect = new_effect
