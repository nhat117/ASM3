import sys
import random
import datetime

# Import the GameState class
from game_state import GameState


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
        self._battle_stats = []

    @property
    def battle_stats(self):
        return self._battle_stats

    @battle_stats.setter
    def battle_stats(self, new_stats):
        self._battle_stats = new_stats

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
        """Display the items in the inventory and allow using an item."""
        if self.inventory:
            print(
                "You are carrying: " + ", ".join([item.name for item in self.inventory])
            )
            # Display in a list
            for index, item in enumerate(self.inventory, start=1):
                print(f"{index}) {item.name} - {item.description}")

            # Allow user to select an item to use
            item_choice = input("Select an item number to use or press Enter to skip: ")
            if item_choice.isdigit():
                item_index = int(item_choice) - 1
                if 0 <= item_index < len(self.inventory):
                    self.use_item(self.inventory[item_index].name)
                else:
                    print("Invalid item number.")
            elif item_choice:
                print("Invalid input.")
        else:
            print("You have no items.")

    def move(self, direction):
        if direction in self.location.doors and self.location.doors[direction]:
            new_location = self.location.doors[direction]
            self.location = new_location
            print(f"You traveled {direction} and arrived at {new_location.name}.")
            # Debug: Print creatures in the new location
            print("Creatures in the new location:")
            for creature in new_location.creatures:
                print(f"- {creature.nickname}")

            # Decrease energy after every 2 moves
            self._move_count += 1
            if self._move_count % 2 == 0:
                self._energy -= 1
                print(
                    f"{self.nickname} lost 1 energy due to movement. Energy: {self._energy}/3"
                )
                if self._energy <= 0:
                    print(
                        f"{self.nickname} is out of energy and escaped into the wild. Game over."
                    )
                    sys.exit(0)
        else:
            raise InvalidDirectionException(f"There is no door to the {direction}.")

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self._energy}/3")

    def challenge(self, creature):
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        wins, losses, draws = 0, 0, 0
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
                    print(
                        f"You lost 1 encounter and lost 1 energy. Energy: {self._energy}/3"
                    )
                else:
                    print(
                        f"You lost 1 encounter but your immunity protected you. Energy: {self._energy}/3"
                    )
                    self._has_immunity = False
            else:
                draws += 1

        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M%p")
        self._battle_stats.append(
            {
                "timestamp": timestamp,
                "opponent": creature.nickname,
                "wins": wins,
                "draws": draws,
                "losses": losses,
            }
        )

        if wins == 2:
            print(
                f"Congrats! You won the battle and adopted a new Pymon called {creature.nickname}!"
            )
        else:
            print("You lost the battle!")

    def display_battle_stats(self):
        total_wins, total_draws, total_losses = 0, 0, 0
        print(f'Pymon Nickname: "{self.nickname}"')
        for i, stat in enumerate(self._battle_stats, start=1):
            print(
                f"Battle {i}, {stat['timestamp']} Opponent: \"{stat['opponent']}\", W: {stat['wins']} D: {stat['draws']} L: {stat['losses']}"
            )
            total_wins += stat["wins"]
            total_draws += stat["draws"]
            total_losses += stat["losses"]
        print(f"Total: W: {total_wins} D: {total_draws} L: {total_losses}")

    def resolve_battle(self, player_choice, opponent_choice):
        """Resolve the rock-paper-scissor battle."""
        outcomes = {
            ("r", "r"): "draw",
            ("r", "p"): "lose",
            ("r", "s"): "win",
            ("p", "r"): "win",
            ("p", "p"): "draw",
            ("p", "s"): "lose",
            ("s", "r"): "lose",
            ("s", "p"): "win",
            ("s", "s"): "draw",
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
                item = next(
                    (i for i in self._inventory if i.name.lower() == item_name.lower()),
                    None,
                )

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
            print(
                f"{self.nickname} used the magic potion and is now immune for one battle."
            )
        elif item.name.lower() == "binocular":
            direction = input(
                "Use binocular to view (current, west, north, east, south): "
            ).lower()
            if direction == "current":
                self.location.inspect()
            elif direction in self.location.doors and self.location.doors[direction]:
                connected_location = self.location.doors[direction]
                print(
                    f"In the {direction}, there is {connected_location.name}: {connected_location.description}"
                )
            else:
                print(f"This direction leads nowhere.")
        else:
            print(f"{item_name} cannot be used.")


# Animal class (inherits Creature)
class Animal(Creature):
    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)

    def inspect(self):
        print(f"Animal {self.nickname}: {self.description}")


# Item class
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

    def load_data(
        self,
        locations_file="locations.csv",
        creatures_file="creatures.csv",
        items_file="items.csv",
    ):
        self._locations = self._load_locations(locations_file)
        self._creatures = self._load_creatures(creatures_file)
        self._load_items(items_file)

    def _load_locations(self, filename):
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

    def _load_creatures(self, filename):
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

    def _load_items(self, filename):
        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                name, description = parts
                item = Item(name.strip(), description.strip())
                random.choice(self._locations).add_item(item)


# Operation class
class Operation:
    def __init__(self, pymon, record):
        self._pymon = pymon
        self._record = record
        # Initialize the GameState
        self._game_state = GameState()

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
        print("\nPlease issue a command to your Pymon:")
        print("1) Inspect Pymon")
        print("2) Inspect current location")
        print("3) Move")
        print("4) Pick an item")
        print("5) View inventory")
        print("6) Challenge a creature")
        print("7) Generate stats")
        print("8) Save game")
        print("9) Load game")
        print("10) Add custom location")
        print("11) Add custom creature")
        print("12) Exit the program")

    def command_multiplexer(self, command):
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
            item = next(
                (i for i in self.pymon.location.items if i.name.lower() == item_name),
                None,
            )
            if item:
                self.pymon.pick_item(item)
            else:
                print(f"There is no {item_name} in this location.")
        elif command == "5":
            self.pymon.view_inventory()
        elif command == "6":
            creature_name = input("Challenge who?: ").lower()
            creature = next(
                (
                    c
                    for c in self.pymon.location.creatures
                    if c.nickname.lower() == creature_name
                ),
                None,
            )
            if creature:
                self.pymon.challenge(creature)
            else:
                print(f"There is no creature named {creature_name} here.")
        elif command == "7":
            self.pymon.display_battle_stats()
        elif command == "8":
            # Use GameState to save the game
            self._game_state.items = {
                item.name: location.name
                for location in self._record.locations
                for item in location.items
            }

            self._game_state.pymons = {
                pymon.nickname: {
                    "location": pymon.location,
                    "stats": pymon.battle_stats if isinstance(pymon, Pymon) else None,
                }
                for pymon in self._record.creatures
            }

            self._game_state.user_pymon = {
                "location": self._pymon.location,
                "stats": self._pymon.battle_stats,
                "inventory": [item.name for item in self._pymon.inventory],
            }

        elif command == "8":  # Use GameState to save the game
            self._game_state.items = {
                item.name: location.name
                for location in self._record.locations
                for item in location.items
            }

            self._game_state.pymons = {
                pymon.nickname: {
                    "location": pymon.location.name,
                    "stats": pymon.battle_stats if isinstance(pymon, Pymon) else None,
                }
                for pymon in self._record.creatures
            }
            self._game_state.user_pymon = {
                "location": self._pymon.location.name,
                "stats": self._pymon.battle_stats,
                "inventory": [item.name for item in self._pymon.inventory],
            }

            self._game_state.save_game()
            print("Game progress saved.")
        elif command == "9":
            # Use GameState to load the game
            self._game_state.load_game()
            print("Game progress loaded.")

        elif command == "10":
            self.add_custom_location()

        elif command == "11":
            self.add_custom_creature()
        elif command == "12":
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
        print(f"Inventory: {', '.join([item.name for item in self._pymon.inventory])}")
        print(f"Location: {self.pymon.location.name}")

    def add_custom_location(self):
        name = input("Enter location name: ")
        description = input("Enter location description: ")

        doors = {}
        for direction in ["west", "north", "east", "south"]:
            connect = (
                input(
                    f"Do you want to connect a location to the {direction}? (yes/no): "
                )
                .strip()
                .lower()
            )
            if connect == "yes":
                doors[direction] = input(f"Enter {direction} door: ").strip()
            else:
                doors[direction] = "None"

        location = Location(name, description)
        location.doors = doors
        self.record.locations.append(location)

        with open("locations.csv", "r") as file:
            lines = file.readlines()

        with open("locations.csv", "a") as file:
            if any(not line.strip() for line in lines):
                file.write(
                    f"{name}, {description}, west = {doors['west']}, north = {doors['north']}, east = {doors['east']}, south = {doors['south']}\n"
                )
            else:
                file.write("\n")
                file.write(
                    f"{name}, {description}, west = {doors['west']}, north = {doors['north']}, east = {doors['east']}, south = {doors['south']}\n"
                )
        print("Custom location added.")

    def add_custom_creature(self):
        nickname = input("Enter creature nickname: ")
        description = input("Enter creature description: ")
        adoptable = input("Is this creature adoptable (yes/no)?: ").lower()
        creature = (
            Pymon(nickname, description)
            if adoptable == "yes"
            else Animal(nickname, description)
        )

        self.record.creatures.append(creature)

        with open("creatures.csv", "r") as file:
            lines = file.readlines()

        with open("creatures.csv", "a") as file:
            if any(not line.strip() for line in lines):
                file.write(f"{nickname}, {description}, {adoptable}\n")
            else:
                file.write("\n")
                file.write(f"{nickname}, {description}, {adoptable}\n")
        print("Custom creature added.")


################ Custom exceptions########3


class InvalidDirectionException(Exception):
    def __init__(self, message):
        message = f"Invalid direction: {message}, please choose from west, north, east, or south."
        super().__init__(message)


class InvalidInputFileFormat(Exception):
    def __init__(self, message):
        message = f"Invalid input file format: {message}"
        super().__init__(message)


############### Main function to run the game ############
if __name__ == "__main__":
    record = Record()
    if len(sys.argv) == 1:
        record.load_data()
    elif len(sys.argv) == 2:
        record.load_data(locations_file=sys.argv[1])
    elif len(sys.argv) == 3:
        record.load_data(locations_file=sys.argv[1], creatures_file=sys.argv[2])
    elif len(sys.argv) == 4:
        record.load_data(
            locations_file=sys.argv[1],
            creatures_file=sys.argv[2],
            items_file=sys.argv[3],
        )

    pymon = Pymon(
        "Kimimon",
        "White and yellow Pymon with a square face",
        random.choice(record.locations),
    )
    operation = Operation(pymon, record)
    operation.menu()
