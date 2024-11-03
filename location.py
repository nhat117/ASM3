
class Location:
    def __init__(self, name, desc):
        """Initialize the Location object."""
        self.__name = name
        self.__desc = desc
        self.__doors = {"west": None, "north": None, "east": None, "south": None}
        self.__creatures = []
        self.__items = []

    @property
    def name(self):
        """Getter for name"""
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def desc(self):
        """Getter for Description"""
        return self.__desc

    @desc.setter
    def desc(self, new_description):
        """Setter for Description"""
        self.__desc = new_description

    @property
    def doors(self):
        """Getter for Doors"""
        return self.__doors

    @doors.setter
    def doors(self, new_doors):
        """Setter for Doors"""
        if isinstance(new_doors, dict):
            self.__doors = new_doors
        else:
            raise ValueError("Doors must be a dictionary")

    @property
    def creatures(self):
        """Getter for the creatures present in the location."""
        return self.__creatures

    @creatures.setter
    def creatures(self, new_creatures):
        """Setter for the creatures present in the location."""
        if isinstance(new_creatures, list):
            self.__creatures = new_creatures
        else:
            raise ValueError("Creatures must be a list")

    @property
    def items(self):
        """Getter for the items present in the location."""
        return self.__items

    @items.setter
    def items(self, new_items):
        """Setter for the items present in the location."""
        if isinstance(new_items, list):
            self.items = new_items
        else:
            raise ValueError("Items must be a list")

    def add_creature(self, creature):
        """Add a creature to the location."""
        self.creatures.append(creature)

    def add_item(self, item):
        """Add an item to the location."""
        self.items.append(item)

    def inspect(self):
        """Inspect the location and display its details."""
        print(f"You are at {self.__name}. {self.__desc}")
        if self.creatures:
            for creature in self.creatures:
                print(f"Creature present: {creature.nickname} - {creature.desc}")
        else:
            print("No creatures here.")
        if self.items:
            for item in self.items:
                print(f"Item present: {item.name} - {item.desc}")
        else:
            print("No items here.")

    def get_item(self, item_name):
        """Get an item from the location."""
        item = None
        for i in self.items:
            if i.name == item_name:
                item = i
                break
        return item

    def validate_new_loc(self, new_name, new_doors, existing_loc):
        """Validate a new location against existing ones."""
        # Check for blank fields
        if not new_name:
            raise ValueError("Location name must be specified.")

        # Ensure at least one direction is not None
        all_none = True
        for direction in new_doors.values():
            if direction is not None:
                all_none = False
                break
        if all_none:
            raise ValueError("At least one direction must be specified.")

        # Check for unique location name
        name_exists = False
        for loc in existing_loc:
            if loc.name == new_name:
                name_exists = True
                break

        if name_exists:
            raise ValueError("Location name must be unique.")

        # Check for similar locations
        for loc in existing_loc:
            if loc.doors == new_doors:
                raise ValueError("A similar location with the same connections already exists.")

        # Check if all specified directions exist
        existing_loc_names = []
        for loc in existing_loc:
            existing_loc_names.append(loc.name)

        for direction, loc_name in new_doors.items():
            if loc_name and loc_name not in existing_loc_names:
                raise ValueError(f"Location in direction {direction} does not exist: {loc_name}")
