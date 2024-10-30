MAX_ENERGY = 3
ENERGY_PLUS_RATE = 1


class Item:
    def __init__(self, name, description, can_be_picked=True, effect=None):
        self._name = name
        self._description = description
        self._can_be_picked = can_be_picked  # Some items can't be picked (e.g., trees)
        self._effect = (
            effect  # Effect of the item (e.g., "restore_energy", "grant_immunity")
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    @property
    def can_be_picked(self):
        return self._can_be_picked

    @can_be_picked.setter
    def can_be_picked(self, new_can_be_picked):
        if isinstance(new_can_be_picked, bool):
            self._can_be_picked = new_can_be_picked
        else:
            raise ValueError("can_be_picked must be a boolean value.")

    @property
    def effect(self):
        return self._effect

    @effect.setter
    def effect(self, new_effect):
        self._effect = new_effect

    def apply(self, pymon):
        """Apply the effect of the item to the Pymon."""
        if self._effect == "restore_energy":
            pymon.energy = min(MAX_ENERGY, pymon.energy + ENERGY_PLUS_RATE)
            print(
                f"{pymon.nickname}'s energy is restored! Energy: {pymon.energy}/{MAX_ENERGY}"
            )
        elif self._effect == "grant_immunity":
            pymon.has_immunity = True
            print(f"{pymon.nickname} is now immune for one battle!")
