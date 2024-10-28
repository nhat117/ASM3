import sys
import random


# Location class
class Location:
    def __init__(self, name, description):
        self._name = name
        self._description = description
        self._doors = {"west": None, "north": None, "east": None, "south": None}
        self._creatures = []
        self._items = []

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

    # Getter and setter for doors
    @property
    def doors(self):
        return self._doors

    @doors.setter
    def doors(self, new_doors):
        if isinstance(new_doors, dict):
            self._doors = new_doors
        else:
            raise ValueError("Doors must be a dictionary")

    # Getter and setter for creatures
    @property
    def creatures(self):
        return self._creatures

    @creatures.setter
    def creatures(self, new_creatures):
        if isinstance(new_creatures, list):
            self._creatures = new_creatures
        else:
            raise ValueError("Creatures must be a list")

    # Getter and setter for items
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
        self._creatures.append(creature)

    def add_item(self, item):
        self._items.append(item)

    def inspect(self):
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


# Creature class
class Creature:
    def __init__(self, nickname, description, location=None):
        self._nickname = nickname
        self._description = description
        self._location = location

    # Getter and setter for nickname
    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, new_nickname):
        self._nickname = new_nickname

    # Getter and setter for description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    # Getter and setter for location
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, new_location):
        self._location = new_location


# Pymon class (inherits Creature)
class Pymon(Creature):
    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)
        self._energy = 3
        self._inventory = []  # Pymon inventory to store items
        self._has_immunity = False
        self._move_count = 0

    # Getter and setter for energy
    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new_energy):
        if 0 <= new_energy <= 3:
            self._energy = new_energy
        else:
            raise ValueError("Energy must be between 0 and 3.")

    # Getter and setter for inventory
    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, new_inventory):
        if isinstance(new_inventory, list):
            self._inventory = new_inventory
        else:
            raise ValueError("Inventory must be a list.")

    # Getter and setter for has_immunity
    @property
    def has_immunity(self):
        return self._has_immunity

    @has_immunity.setter
    def has_immunity(self, new_immunity):
        if isinstance(new_immunity, bool):
            self._has_immunity = new_immunity
        else:
            raise ValueError("has_immunity must be a boolean value.")

    @property
    def move_count(self):
        return self._move_count

    @move_count.setter
    def move_count(self, new_move_count):
        self._move_count = new_move_count

    def pick_item(self, item):
        """Attempt to pick up an item."""
        if item.can_be_picked:
            self.inventory.append(item)
            print(f"You picked up {item.name} from the ground!")
        else:
            print(f"The {item.name} cannot be picked up.")

    def view_inventory(self):
        """Display the items in the inventory."""
        if self.inventory:
            print("You are carrying: " + ', '.join([item.name for item in self.inventory]))
            # Display in a list
            for index, item in enumerate(self.inventory, start=1):
                print(f"{index}) {item.name} - {item.description}")
        else:
            print("You have no items.")

    def move(self, direction):
        if direction in self.location.doors and self.location.doors[direction]:
            new_location = self.location.doors[direction]
            self.location = new_location
            print(f"You traveled {direction} and arrived at {new_location.name}.")

            # Decrease energy after every 2 moves
            self._move_count += 1
            if self._move_count % 2 == 0:
                self._energy -= 1
                print(f"{self.nickname} lost 1 energy due to movement. Energy: {self._energy}/3")
                if self._energy <= 0:
                    print(f"{self.nickname} is out of energy and escaped into the wild. Game over.")
                    sys.exit(0)
        else:
            raise InvalidDirectionException(f"There is no door to the {direction}.")

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self._energy}/3")

    def challenge(self, creature):
        """Challenge another Pymon to a battle."""
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        wins, losses = 0, 0
        while wins < 2 and losses < 2 and self._energy > 0:
            player_choice = input("Your turn (r)ock, (p)aper, or (s)cissor?: ").lower()
            if player_choice not in ["r", "p", "s"]:
                print("Invalid choice, please choose r, p, or s.")
                continue
            opponent_choice = random.choice(["r", "p", "s"])
            print(f"Your opponent issued {opponent_choice}!")
            result = self.resolve_battle(player_choice, opponent_choice)
            if result == "win":
                wins += 1
                print(f"You won 1 encounter!")
            elif result == "lose":
                losses += 1
                if not self._has_immunity:
                    self._energy -= 1
                    print(f"You lost 1 encounter and lost 1 energy. Energy: {self._energy}/3")
                else:
                    print(f"You lost 1 encounter but your immunity protected you. Energy: {self._energy}/3")
                    self._has_immunity = False

        if wins == 2:
            print(f"Congrats! You won the battle and adopted a new Pymon called {creature.nickname}!")
        else:
            print("You lost the battle!")

    def resolve_battle(self, player_choice, opponent_choice):
        """Resolve the rock-paper-scissor battle."""
        outcomes = {
            ('r', 'r'): 'draw', ('r', 'p'): 'lose', ('r', 's'): 'win',
            ('p', 'r'): 'win', ('p', 'p'): 'draw', ('p', 's'): 'lose',
            ('s', 'r'): 'lose', ('s', 'p'): 'win', ('s', 's'): 'draw'
        }
        return outcomes.get((player_choice, opponent_choice))

    def use_item(self, item_name):
        """Use an item from the inventory."""
        item = None
        for index, i in enumerate(self._inventory, start=1):
            try:
                if index == int(item_name):
                    item = i
            except ValueError:
                item = next((i for i in self._inventory if i.name.lower() == item_name.lower()), None)

        if not item:
            print(f"No item named {item_name} in the inventory.")
            return

        if item.name.lower() == "apple":
            if self._energy < 3:
                self._energy = min(3, self._energy + 1)
                self._inventory.remove(item)
                print(f"{self.nickname} ate the apple. Energy: {self._energy}/3")
            else:
                print(f"{self.nickname} is already at full energy.")
        elif item.name.lower() == "magic potion":
            self._has_immunity = True
            self._inventory.remove(item)
            print(f"{self.nickname} used the magic potion and is now immune for one battle.")
        elif item.name.lower() == "binocular":
            direction = input("Use binocular to view (current, west, north, east, south): ").lower()
            if direction == "current":
                self.location.inspect()
            elif direction in self.location.doors and self.location.doors[direction]:
                connected_location = self.location.doors[direction]
                print(
                    f"In the {direction}, there is {connected_location.name()}: {connected_location.description()}")
            else:
                print(f"This direction leads nowhere.")
        else:
            print(f"{item_name} cannot be used.")


# Item class
class Item:
    def __init__(self, name, description, can_be_picked=True, effect=None):
        self._name = name
        self._description = description
        self._can_be_picked = can_be_picked  # Some items can't be picked (e.g., trees)
        self._effect = effect  # Effect of the item (e.g., "restore_energy", "grant_immunity")

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


# Record class to load initial locations and creatures
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

    def load_data(self):
        """Load data for locations and creatures."""
        # Create locations
        playground = Location("Playground", "A place to play and have fun.")
        beach = Location("Beach", "A sunny place with soft sand.")
        school = Location("School", "A secondary school for local creatures.")

        # Create connections between locations
        playground.connect("north", beach)
        playground.connect("east", school)

        # Add creatures
        creature1 = Creature("Large Pymon", "White and blue large Pymon", playground)
        creature2 = Creature("Small Pymon", "Yellow and orange small Pymon", school)
        playground.add_creature(creature1)
        school.add_creature(creature2)

        # Add items
        playground.add_item(Item("Magic Potion", "Grants immunity for one battle", effect="grant_immunity"))
        beach.add_item(Item("Apple", "Replenishes Pymon's energy", effect="restore_energy"))
        school.add_item(Item("Binocular", "Allows quick review of surroundings"))
        playground.add_item(Item("Tree", "Just a tree, cannot be picked up", can_be_picked=False))

        # Use the setters for locations and creatures
        self.locations = [playground, beach, school]
        self.creatures = [creature1, creature2]


# Operation class
class Operation:
    def __init__(self, pymon, record):
        self._pymon = pymon
        self._record = record

    # Getter and setter for pymon
    @property
    def pymon(self):
        return self._pymon

    @pymon.setter
    def pymon(self, new_pymon):
        self._pymon = new_pymon

    # Getter and setter for record
    @property
    def record(self):
        return self._record

    @record.setter
    def record(self, new_record):
        self._record = new_record

    def display_menu(self):
        """Display the menu options."""
        print("\nPlease issue a command to your Pymon:")
        print("1) Inspect Pymon")
        print("2) Inspect current location")
        print("3) Move")
        print("4) Pick an item")
        print("5) View inventory")
        print("6) Challenge a creature")
        print("7) Generate stats")
        print("8) Exit the program")

    def command_multiplexer(self, command):
        """Execute the command based on user input."""
        if command == "1":
            self.pymon.inspect()
        elif command == "2":
            self.pymon.location.inspect()
        elif command == "3":
            direction = input("Moving to which direction?: ").lower()
            try:
                self.pymon.move(direction)
            except InvalidDirectionException as e:
                print(e)
        elif command == "4":
            item_name = input("Picking what item?: ").lower()
            item = next((i for i in self.pymon.location.items if i.name.lower() == item_name), None)
            if item:
                self.pymon.pick_item(item)
            else:
                print(f"There is no {item_name} in this location.")
        elif command == "5":
            if not self.pymon.inventory:
                print("You have no items.")
                input("Press Enter to continue...")
                return
            input("a) Select item to use ").lower()
            self.pymon.view_inventory()

            sub_command = input("Select an item or 'back' to return): ").lower()
            if sub_command != 'back':
                self.pymon.use_item(sub_command)
        elif command == "6":
            creature_name = input("Challenge who?: ").lower()
            creature = next((c for c in self.pymon.location.creatures if c.nickname.lower() == creature_name), None)
            if creature:
                self.pymon.challenge(creature)
            else:
                print(f"There is no creature named {creature_name} here.")
        elif command == "7":
            self.generate_stats()
        elif command == "8":
            print("Exiting the program.")
            sys.exit(0)
        else:
            print("Invalid command, please try again.")

    def menu(self):
        while True:
            self.display_menu()
            command = input("Enter your command: ")
            self.command_multiplexer(command)

    def generate_stats(self):
        """Generate and display stats."""
        print(f"Pymon {self.pymon.nickname} Stats:")
        print(f"Energy: {self.pymon.energy}/3")
        print(f"Inventory: {', '.join([item.name for item in self.pymon.inventory])}")
        print(f"Location: {self.pymon.location.name}")


################ Custom exceptions########3


class InvalidDirectionException(Exception):
    def __init__(self, message):
        message = f"Invalid direction: {message}, please choose from west, north, east, or south."
        super().__init__(message)


class InvalidInputFileFormat(Exception):
    def __init__(self, message):
        message = f"Invalid input file format: {message}"
        super().__init__(message)


############ Main function to run the game#########
if __name__ == "__main__":
    # Setup locations, creatures, and Pymon
    record = Record()
    record.load_data()

    # Place the Pymon in the playground initially
    pymon = Pymon("Kimimon", "White and yellow Pymon with a square face", record.locations[0])

    # Start the game
    operation = Operation(pymon, record)
    operation.menu()
