import sys

# Import the GameState class
from game_state import GameState
from location import Location
from creature import Pymon, Animal
from exceptions import InvalidDirectionException


# Operation class
class Operation:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one Operation instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pymon, record):
        """Initialize Operation with a Pymon and game record."""
        if not hasattr(self, "_initialized"):  # To prevent reinitialization
            self._pymon = pymon
            self._record = record
            self._game_state = GameState()
            self._initialized = True  # Mark as initialized to avoid reinitialization

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

    def display_setup(self):
        """
        Display the current setup of the game world including locations, connections,
        items, and creatures.
        """
        print("\n=== Game World Setup ===\n")

        # Display Locations and their connections
        print("=== Locations ===")
        for location in self._record.locations:
            print(f"\nLocation: {location.name}")
            print(f"Description: {location.description}")
            print("Connections:")
            if location.doors:
                has_connections = False
                for direction, connected_loc in location.doors.items():
                    if connected_loc and connected_loc != "None":
                        has_connections = True
                        # If connected_loc is a Location object, use its name
                        loc_name = (
                            connected_loc.name
                            if isinstance(connected_loc, Location)
                            else connected_loc
                        )
                        print(f"  {direction} -> {loc_name}")
                if not has_connections:
                    print("  No connections")
            else:
                print("  No connections")

        # Display Items
        print("\n=== Items ===")
        for location in self._record.locations:
            for item in location.items:
                print(f"\nItem: {item.name}")
                print(f"Location: {location.name}")
                print(f"Can be picked: {item.can_be_picked}")

        # Display Creatures
        print("\n=== Creatures ===")
        for creature in self._record.creatures:
            print(f"\nCreature: {creature.nickname}")
            print(f"Description: {creature.description}")
            print(
                f"Location: {creature.location.name if creature.location else 'Unknown'}"
            )
            print(f"Is Pymon: {isinstance(creature, Pymon)}")

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
        print("12) Display setup")
        print("13) View bench Pymons")
        print("14) Switch active Pymon")
        print("15) Exit the program")

    def command_multiplexer(self, command):
        commands = {
            "1": self.inspect_pymon,
            "2": self.inspect_location,
            "3": self.move_pymon,
            "4": self.pick_item,
            "5": self.view_inventory,
            "6": self.challenge_creature,
            "7": self.display_battle_stats,
            "8": self.save_game,
            "9": self.load_game,
            "10": self.add_custom_location,
            "11": self.add_custom_creature,
            "12": self.display_setup,
            "13": self.view_bench_pymons,
            "14": self.switch_active_pymon,
            "15": self.exit_program,
        }

        if command in commands:
            commands[command]()
        else:
            print("Invalid command, please try again.")

    def inspect_pymon(self):
        self.pymon.inspect()

    def inspect_location(self):
        self.pymon.location.inspect()

    def move_pymon(self):
        direction = input("Moving to which direction?: ").lower()
        try:
            needs_switch = self.pymon.move(direction, self._game_state)
            if needs_switch:
                self.force_switch_pymon()
        except InvalidDirectionException as e:
            print(e)

    def pick_item(self):
        item_name = input("Picking what item?: ").lower()
        item = next(
            (i for i in self.pymon.location.items if i.name.lower() == item_name), None
        )
        if item:
            self.pymon.pick_item(item)
        else:
            print(f"There is no {item_name} in this location.")

    def view_inventory(self):
        self.pymon.view_inventory()

    def challenge_creature(self):
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
            captured_pymon = self.pymon.challenge(creature)
            if captured_pymon and isinstance(captured_pymon, Pymon):
                self._game_state.bench_pymons.append(
                    {
                        "nickname": captured_pymon.nickname,
                        "description": captured_pymon.description,
                        "inventory": [],
                        "stats": {
                            "energy": 3,
                            "has_immunity": False,
                            "move_count": 0,
                            "battle_stats": [],
                        },
                    }
                )
                print(f"{captured_pymon.nickname} has been added to your bench!")
        else:
            print(f"There is no creature named {creature_name} here.")

    def display_battle_stats(self):
        self.pymon.display_battle_stats()

    def save_game(self):
        save_file = input("Enter save file name (default: save2024.csv): ").strip()
        if not save_file:
            save_file = "save2024.csv"
        self._record.save_game_state(save_file, self._pymon)
        print(f"Game progress saved to {save_file}")

    def load_game(self):
        save_file = input(
            "Enter save file name to load (default: save2024.csv): "
        ).strip()
        if not save_file:
            save_file = "save2024.csv"

        try:
            loaded_pymon = self._record.load_game_state(save_file)
            if loaded_pymon:
                self._pymon = loaded_pymon
                self._game_state = self._record._game_state
                print(f"Game progress loaded from {save_file}")
                self.generate_stats()
            else:
                print(
                    "No valid saved game data found. Starting with current Pymon state."
                )
                self.generate_stats()
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            print("Starting with current Pymon state.")
            self.generate_stats()

    def exit_program(self):
        print("Exiting the program.")
        sys.exit(0)

    def force_switch_pymon(self):
        """Force switch to a Pymon with energy when current Pymon runs out of energy."""
        while True:
            index = self.get_pymon_choice()
            if index is not None:
                selected_pymon = self._game_state.bench_pymons[index]
                if self.pymon_has_energy(selected_pymon):
                    self.switch_to_pymon(index, selected_pymon)
                    return
                else:
                    print("That Pymon has no energy! Choose another one.")

    def get_pymon_choice(self):
        """Prompt user to select a Pymon and return the corresponding index."""
        choice = input("Enter the number of the Pymon you want to switch to: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(self._game_state.bench_pymons):
                return index
            else:
                print("Invalid Pymon number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        return None

    def pymon_has_energy(self, pymon):
        """Check if the selected Pymon has energy."""
        return "stats" in pymon and pymon["stats"].get("energy", 0) > 0

    def switch_to_pymon(self, index, selected_pymon):
        """Switch to the selected Pymon, update stats and inventory."""
        current_pymon_data = self.save_current_pymon_data()

        new_pymon = self.create_new_pymon(selected_pymon)

        # Set up new Pymon's stats and inventory
        self.set_pymon_stats(new_pymon, selected_pymon)
        self.set_pymon_inventory(new_pymon, selected_pymon)

        # Update the bench with the current Pymon data
        self._game_state.bench_pymons[index] = current_pymon_data

        # Switch active Pymon
        self._pymon = new_pymon
        print(f"\nSwitched to {new_pymon.nickname}!")
        print(f"Energy: {new_pymon.energy}/3")

    def save_current_pymon_data(self):
        """Save the current Pymon's data to the bench."""
        return {
            "nickname": self._pymon.nickname,
            "description": self._pymon.description,
            "inventory": [item.name for item in self._pymon.inventory],
            "stats": {
                "energy": self._pymon.energy,
                "has_immunity": self._pymon.has_immunity,
                "move_count": self._pymon.move_count,
                "battle_stats": self._pymon.battle_stats,
            },
        }

    def create_new_pymon(self, selected_pymon):
        """Create a new Pymon instance from the selected Pymon."""
        return Pymon(
            selected_pymon["nickname"],
            selected_pymon["description"],
            self._pymon.location,
        )

    def set_pymon_stats(self, new_pymon, selected_pymon):
        """Set the stats for the new Pymon."""
        if "stats" in selected_pymon:
            new_pymon.energy = selected_pymon["stats"].get("energy", 3)
            new_pymon.has_immunity = selected_pymon["stats"].get("has_immunity", False)
            new_pymon.move_count = selected_pymon["stats"].get("move_count", 0)
            new_pymon.battle_stats = selected_pymon["stats"].get("battle_stats", [])

    def set_pymon_inventory(self, new_pymon, selected_pymon):
        """Set the inventory for the new Pymon."""
        if selected_pymon.get("inventory"):
            for item_name in selected_pymon["inventory"]:
                for location in self._record.locations:
                    item = next(
                        (i for i in location.items if i.name == item_name), None
                    )
                    if item:
                        new_pymon.inventory.append(item)
                        location.items.remove(item)
                        break

    def view_bench_pymons(self):
        """Display all Pymons on the bench."""
        if not self._game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return

        print("\n=== Your Bench Pymons ===")
        for i, pymon in enumerate(self._game_state.bench_pymons, 1):
            print(f"\n{i}) {pymon['nickname']}")
            print(f"   Description: {pymon['description']}")
            if "stats" in pymon:
                print(f"   Energy: {pymon['stats'].get('energy', 3)}/3")
            if pymon.get("inventory"):
                print(f"   Inventory: {', '.join(pymon['inventory'])}")

    def switch_active_pymon(self):
        """Switch the currently active Pymon with one from the bench."""
        if not self._game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return

        self.view_bench_pymons()
        choice = self.get_pymon_switch_choice()
        if choice is not None:
            selected_pymon = self._game_state.bench_pymons[choice]
            current_pymon_data = self.save_current_pymon_data()
            new_pymon = self.create_new_pymon(selected_pymon)

            self.set_pymon_stats(new_pymon, selected_pymon)
            self.set_pymon_inventory(new_pymon, selected_pymon)
            self.update_bench(choice, current_pymon_data)

            self._pymon = new_pymon
            self.display_switch_success(new_pymon)

    def get_pymon_switch_choice(self):
        """Prompt user for the Pymon they want to switch to."""
        choice = input(
            "\nEnter the number of the Pymon you want to switch to (or press Enter to cancel): "
        )
        if not choice:
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(self._game_state.bench_pymons):
                return index
            else:
                print("Invalid Pymon number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        return None

    def update_bench(self, index, current_pymon_data):
        """Update the bench with the current Pymon's data."""
        self._game_state.bench_pymons[index] = current_pymon_data

    def display_switch_success(self, new_pymon):
        """Display success message after switching to a new Pymon."""
        print(f"\nSwitched to {new_pymon.nickname}!")
        print(f"Energy: {new_pymon.energy}/3")
        if new_pymon.inventory:
            print(
                f"Current inventory: {', '.join(item.name for item in new_pymon.inventory)}"
            )
        else:
            print("Current inventory is empty.")

    def menu(self):
        while True:
            self.display_menu()
            command = input("Enter your command: ")
            self.command_multiplexer(command)

    def generate_stats(self):
        """Generate and display stats."""
        print(f"\nPymon {self.pymon.nickname} Stats:")
        print(f"Description: {self.pymon.description}")
        print(f"Energy: {self.pymon.energy}/3")
        print(f"Inventory: {', '.join([item.name for item in self.pymon.inventory])}")
        print(
            f"Location: {self.pymon.location.name if self.pymon.location else 'None'}"
        )
        print(f"Has Immunity: {'Yes' if self.pymon.has_immunity else 'No'}")
        print(f"Move Count: {self.pymon.move_count}")
        if self.pymon.battle_stats:
            print("\nBattle History:")
            self.pymon.display_battle_stats()

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
