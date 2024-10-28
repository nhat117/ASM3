import sys
import random


# Location class
class Location:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.doors = {"west": None, "north": None, "east": None, "south": None}
        self.creatures = []
        self.items = []

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

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
        self.creatures.append(creature)

    def add_item(self, item):
        self.items.append(item)

    def inspect(self):
        print(f"You are at {self.name}. {self.description}")
        if self.creatures:
            for creature in self.creatures:
                print(f"Creature present: {creature.nickname} - {creature.description}")
        else:
            print("No creatures here.")
        if self.items:
            for item in self.items:
                print(f"Item present: {item.name} - {item.description}")
        else:
            print("No items here.")


# Creature class
class Creature:
    def __init__(self, nickname, description, location=None):
        self.nickname = nickname
        self.description = description
        self.location = location


# Pymon class (inherits Creature)
class Pymon(Creature):
    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)
        self.energy = 3
        self.inventory = []  # Pymon inventory to store items
        self.has_immunity = False

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
        else:
            print("You have no items.")

    def move(self, direction):
        if direction in self.location.doors and self.location.doors[direction]:
            new_location = self.location.doors[direction]
            self.location = new_location
            print(f"You traveled {direction} and arrived at {new_location.get_name()}.")
        else:
            raise InvalidDirectionException(
                f"There is no door to the {direction}. Pymon remains at its current location.")

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self.energy}/3")

    def challenge(self, creature):
        """Challenge another Pymon to a battle."""
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        wins, losses = 0, 0
        while wins < 2 and losses < 2 and self.energy > 0:
            player_choice = input("Your turn (r)ock, (p)aper, or (s)cissor?: ").lower()
            opponent_choice = random.choice(["r", "p", "s"])
            print(f"Your opponent issued {opponent_choice}!")
            result = self.resolve_battle(player_choice, opponent_choice)
            if result == "win":
                wins += 1
                print(f"You won 1 encounter!")
            elif result == "lose":
                losses += 1
                if not self.has_immunity:
                    self.energy -= 1
                    print(f"You lost 1 encounter and lost 1 energy. Energy: {self.energy}/3")
                else:
                    print(f"You lost 1 encounter but your immunity protected you. Energy: {self.energy}/3")
                    self.has_immunity = False

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
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            print(f"No item named {item_name} in the inventory.")
            return

        if item.name.lower() == "apple":
            if self.energy < 3:
                self.energy = min(3, self.energy + 1)
                self.inventory.remove(item)
                print(f"{self.nickname} ate the apple. Energy: {self.energy}/3")
            else:
                print(f"{self.nickname} is already at full energy.")
        elif item.name.lower() == "magic potion":
            self.has_immunity = True
            self.inventory.remove(item)
            print(f"{self.nickname} used the magic potion and is now immune for one battle.")
        elif item.name.lower() == "binocular":
            direction = input("Use binocular to view (current, west, north, east, south): ").lower()
            if direction == "current":
                self.location.inspect()
            elif direction in self.location.doors and self.location.doors[direction]:
                connected_location = self.location.doors[direction]
                print(
                    f"In the {direction}, there is {connected_location.get_name()}: {connected_location.get_description()}")
            else:
                print(f"This direction leads nowhere.")
        else:
            print(f"{item_name} cannot be used.")


# Item class
class Item:
    def __init__(self, name, description, can_be_picked=True, effect=None):
        self.name = name
        self.description = description
        self.can_be_picked = can_be_picked  # Some items can't be picked (e.g., trees)
        self.effect = effect  # Effect of the item (e.g., "restore_energy", "grant_immunity")

    def apply(self, pymon):
        """Apply the effect of the item to the Pymon."""
        if self.effect == "restore_energy":
            pymon.energy = min(3, pymon.energy + 1)
            print(f"{pymon.nickname}'s energy is restored! Energy: {pymon.energy}/3")
        elif self.effect == "grant_immunity":
            pymon.has_immunity = True
            print(f"{pymon.nickname} is now immune for one battle!")


# Record class to load initial locations and creatures
class Record:
    def __init__(self):
        self.locations = []
        self.creatures = []

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

        self.locations = [playground, beach, school]
        self.creatures = [creature1, creature2]


# Operation class
class Operation:
    def __init__(self, pymon, record):
        self.pymon = pymon
        self.record = record

    def display_menu(self):
        """Display the menu options."""
        print("\nPlease issue a command to your Pymon:")
        print("1) Inspect Pymon")
        print("2) Inspect current location")
        print("3) Move")
        print("4) Pick an item")
        print("5) View inventory")
        print("6) Challenge a creature")
        print("7) Use an item")
        print("8) Exit the program")

    def get_command(self):
        """Get the command from the user."""
        return input("Your command: ")

    def menu(self):
        """Provide options for the player to choose."""
        while True:
            self.display_menu()
            command = self.get_command()
            self.command_multiplexer(command)

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
            # Find the item in the current location
            item = next((i for i in self.pymon.location.items if i.name.lower() == item_name), None)
            if item:
                self.pymon.pick_item(item)
            else:
                print(f"There is no {item_name} in this location.")
        elif command == "5":
            self.pymon.view_inventory()
        elif command == "6":
            creature_name = input("Challenge who?: ").lower()
            creature = next((c for c in self.pymon.location.creatures if c.nickname.lower() == creature_name), None)
            if creature:
                self.pymon.challenge(creature)
            else:
                print(f"There is no creature named {creature_name} here.")
        elif command == "7":
            item_name = input("Using what item?: ").lower()
            try:
                self.pymon.use_item(item_name)
            except InvalidDirectionException as e:
                print(e)
        elif command == "8":
            print("Exiting the program.")
            sys.exit(0)
        else:
            print("Invalid command, please try again.")


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
