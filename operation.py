import sys

# Import the GameState class
from game_state import GameState
from location import Location
from creature import Pymon, Animal
from exceptions import InvalidDirectionException, AnimalCaptureError
from item import MAX_ENERGY


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
        """Getter for the Pymon."""
        return self._pymon

    @pymon.setter
    def pymon(self, new_pymon):
        self._pymon = new_pymon

    # Getter and setter for record
    @property
    def record(self):
        """Getter for the game record."""
        return self._record

    @record.setter
    def record(self, new_record):
        self._record = new_record

    @property
    def game_state(self):
        """Getter for the game state."""
        return self._game_state

    @game_state.setter
    def game_state(self, new_game_state):
        self._game_state = new_game_state

    def display_setup(self):
        """
        Display the current setup of the game world including locations, connections,
        items, and creatures.
        """
        print("\n###### Game World Setup ##########\n")

        # Display Locations and their connections
        print("###### Locations ##########")
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
        print("\n###### Items ##########")
        for location in self._record.locations:
            for item in location.items:
                print(f"\nItem: {item.name}")
                print(f"Location: {location.name}")
                print(f"Can be picked: {item.can_be_picked}")

        # Display Creatures
        print("\n###### Creatures ##########")
        for creature in self._record.creatures:
            print(f"\nCreature: {creature.nickname}")
            print(f"Description: {creature.description}")
            print(
                f"Location: {creature.location.name if creature.location else 'Unknown'}"
            )
            print(f"Is Pymon: {isinstance(creature, Pymon)}")

    def display_menu(self):
        """Display the menu options for the game."""
        print("##########################################")
        print("############## Pymon Game ################")
        print("##########################################")
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
        print("13) Exit the program")

    def command_multiplexer(self, command):
        """Multiplex the command to the corresponding function."""
        try:
            user_command = int(command)
            if user_command == 1:
                self.inspect_pymon_submenu()
            elif user_command == 2:
                self.pymon.location.inspect()
            elif user_command == 3:
                self.move_pymon()
            elif user_command == 4:
                self.pick_item()
            elif user_command == 5:
                self.view_inventory()
            elif user_command == 6:
                self.challenge_creature()
            elif user_command == 7:
                self.display_battle_stats()
            elif user_command == 8:
                self.save_game()
            elif user_command == 9:
                self.load_game()
            elif user_command == 10:
                self.add_custom_location()
            elif user_command == 11:
                self.add_custom_creature()
            elif user_command == 12:
                self.display_setup()
            elif user_command == 13:
                self.quit()
            else:
                print("Invalid command. Please enter a valid number.")
        except ValueError:
            print("Invalid command. Please enter a valid number.")

    def inspect_pymon_submenu(self):
        """Display submenu for Inspect Pymon."""
        print("\n1.1) Inspect current Pymon")
        print("1.2) Switch active Pymon")
        sub_command = input("Enter your sub-command: ")
        if sub_command == "1.1":
            self.pymon.inspect()
        elif sub_command == "1.2":
            self.view_pymons()
            self.switch_active_pymon()
        else:
            print("Invalid sub-command. Please enter a valid number.")

    def move_pymon(self):
        """Move Pymon to a new location."""
        direction = input("Moving to which direction?: ").lower()
        try:
            needs_switch = self.pymon.move(direction, self._game_state)
            if needs_switch:
                self.switch_pymon_compulsory()
        except InvalidDirectionException as e:
            print(e)

    def pick_item(self):
        """Pick an item from the current location."""
        item_name = input("Picking what item?: ").lower()
        item = next(
            (i for i in self.pymon.location.items if i.name.lower() == item_name), None
        )
        if item:
            self.pymon.pick_item(item)
        else:
            print(f"There is no {item_name} in this location.")

    def view_inventory(self):
        """Display the inventory of the Pymon."""
        self.pymon.view_inventory()

    def challenge_creature(self):
        """Challenge a creature in the current location."""
        creature_name = input("Challenge who?: ").lower()
        creature = None
        for c in self.pymon.location.creatures:
            if c.nickname.lower() == creature_name:
                creature = c
                break
        if creature:
            try:
                if isinstance(creature, Animal):
                    print(f"The {creature.nickname} just ignored you.")
                    return

                captured_pymon = self.pymon.challenge(creature)
                if captured_pymon and isinstance(captured_pymon, Pymon):
                    self._game_state.bench_pymons.append(
                        {
                            "nickname": captured_pymon.nickname,
                            "description": captured_pymon.description,
                            "inventory": [],
                            "stats": {
                                "energy": MAX_ENERGY,
                                "has_immunity": False,
                                "move_count": 0,
                                "battle_stats": [],
                            },
                        }
                    )
                    print(f"{captured_pymon.nickname} has been added to your bench!")
            except AnimalCaptureError as e:
                print(e)
        else:
            print(f"There is no creature named {creature_name} here.")

    def display_battle_stats(self):
        """Display the battle stats of the Pymon."""
        self.pymon.display_battle_stats()

    def save_game(self):
        """Save the current game state."""
        save_file = input("Enter save file name (default: save2024.csv): ").strip()
        if not save_file:
            save_file = "save2024.csv"
        self._record.save_game_state(save_file, self._pymon)
        print(f"Game progress saved to {save_file}")

    def load_game(self):
        """Load a saved game state."""
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

    def quit(self):
        """Exit the program."""
        print("Exiting the program.")
        sys.exit(0)

    def switch_pymon_compulsory(self):
        """Force switch to a Pymon with energy when current Pymon runs out of energy."""
        while True:
            index = self.get_user_pymon()
            if index is not None:
                selected_pymon = self._game_state.bench_pymons[index]
                if self.check_energy(selected_pymon):
                    self.switch_pymon(index, selected_pymon)
                    return
                else:
                    print("That Pymon has no energy! Choose another one.")

    def get_user_pymon(self):
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

    def check_energy(self, pymon):
        """Check if the selected Pymon has energy."""
        return "stats" in pymon and pymon["stats"].get("energy", 0) > 0

    def switch_pymon(self, index, selected_pymon):
        """Switch to the selected Pymon, update stats and inventory."""
        current_pymon_data = self.save_current_pymon()

        new_pymon = self.create_new_pymon(selected_pymon)

        # Set up new Pymon's stats and inventory
        self.set_stats(new_pymon, selected_pymon)
        self.set_inventory(new_pymon, selected_pymon)

        # Update the bench with the current Pymon data
        self.game_state.bench_pymons[index] = current_pymon_data

        # Switch active Pymon
        self.pymon = new_pymon
        print(f"\nSwitched to {new_pymon.nickname}!")
        print(f"Energy: {new_pymon.energy}/{MAX_ENERGY}")

    def save_current_pymon(self):
        """Save the current Pymon's data to the bench."""
        return {
            "nickname": self.pymon.nickname,
            "description": self.pymon.description,
            "inventory": [item.name for item in self.pymon.inventory],
            "stats": {
                "energy": self.pymon.energy,
                "has_immunity": self.pymon.has_immunity,
                "move_count": self.pymon.move_count,
                "battle_stats": self.pymon.battle_stats,
            },
        }

    def create_new_pymon(self, selected_pymon):
        """Create a new Pymon instance from the selected Pymon."""
        return Pymon(
            selected_pymon["nickname"],
            selected_pymon["description"],
            self.pymon.location,
        )

    def set_stats(self, new_pymon, selected_pymon):
        """Set the stats for the new Pymon."""
        if "stats" in selected_pymon:
            new_pymon.energy = selected_pymon["stats"].get("energy", 3)
            new_pymon.has_immunity = selected_pymon["stats"].get("has_immunity", False)
            new_pymon.move_count = selected_pymon["stats"].get("move_count", 0)
            new_pymon.battle_stats = selected_pymon["stats"].get("battle_stats", [])

    def set_inventory(self, new_pymon, selected_pymon):
        """Set the inventory for the new Pymon."""
        if selected_pymon.get("inventory"):
            for item_name in selected_pymon["inventory"]:
                for location in self.record.locations:
                    item = next(
                        (i for i in location.items if i.name == item_name), None
                    )
                    if item:
                        new_pymon.inventory.append(item)
                        location.items.remove(item)
                        break

    def view_pymons(self):
        """Display all Pymons on the bench."""
        if not self.game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return

        print("\n=== Your Bench Pymons ===")
        for i, pymon in enumerate(self.game_state.bench_pymons, 1):
            print(f"\n{i}) {pymon['nickname']}")
            print(f"   Description: {pymon['description']}")
            if "stats" in pymon:
                print(f"   Energy: {pymon['stats'].get('energy', 3)}/3")
            if pymon.get("inventory"):
                print(f"   Inventory: {', '.join(pymon['inventory'])}")

    def switch_active_pymon(self):
        """Switch the currently active Pymon with one from the bench."""
        if not self.game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return

        self.view_pymons()
        choice = self.get_pymon_switch_choice()
        if choice is not None:
            selected_pymon = self.game_state.bench_pymons[choice]
            current_pymon_data = self.save_current_pymon()
            new_pymon = self.create_new_pymon(selected_pymon)

            self.set_stats(new_pymon, selected_pymon)
            self.set_inventory(new_pymon, selected_pymon)
            self.update_bench(choice, current_pymon_data)

            self.pymon = new_pymon
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
            if 0 <= index < len(self.game_state.bench_pymons):
                return index
            else:
                print("Invalid Pymon number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        return None

    def update_bench(self, index, current_pymon_data):
        """Update the bench with the current Pymon's data."""
        self.game_state.bench_pymons[index] = current_pymon_data

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
            input("Press enter to continue")

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
        """Handle add custom location"""
        # Get location details with validation for blank fields
        name = input("Enter location name: ").strip()
        if not name:
            print("Error: Location name cannot be blank")
            return

        description = input("Enter location description: ").strip()
        if not description:
            print("Error: Location description cannot be blank")
            return

        # Initialize doors dictionary
        doors = {"west": None, "north": None, "east": None, "south": None}
        has_connection = False

        # Get door connections
        for direction in ["west", "north", "east", "south"]:
            connect = input(f"Do you want to connect a location to the {direction}? (yes/no): ").strip().lower()
            if connect == "yes":
                connected_loc = input(f"Enter {direction} door: ").strip()
                if connected_loc:
                    doors[direction] = connected_loc
                    has_connection = True
                else:
                    print(f"Error: Connected location name cannot be blank")
                    return

        # Ensure at least one connection is specified
        if not has_connection:
            print("Error: At least one connection must be specified")
            return

        try:
            # Create and validate the new location
            location_instance = Location(name, description)
            location_instance.validate_new_location(name, doors, self.record.locations)

            # Create the new location and add it to record
            new_loc = Location(name, description)
            new_loc.doors = doors
            self.record.locations.append(new_loc)

            # Update the CSV file with bi-directional connections
            self.update_locations_csv(new_loc)
            print("Custom location added successfully.")

        except ValueError as e:
            print(f"Error: {str(e)}")

    def update_locations_csv(self, new_location):
        """Update the locations.csv file with the new location and update bi-directional connections"""
        # Read existing locations
        with open("locations.csv", "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        # Update existing locations for bi-directional connections
        updated_lines = []
        for line in lines:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) >= 6:  # Ensure line has all required parts
                loc_name = parts[0]
                loc_desc = parts[1]
                doors = {
                    "west": parts[2].split('=')[1].strip(),
                    "north": parts[3].split('=')[1].strip(),
                    "east": parts[4].split('=')[1].strip(),
                    "south": parts[5].split('=')[1].strip()
                }

                # Update bi-directional connections
                for direction, connected_loc in new_location.doors.items():
                    if connected_loc == loc_name:
                        opposite_direction = {
                            "west": "east",
                            "east": "west",
                            "north": "south",
                            "south": "north"
                        }[direction]
                        doors[opposite_direction] = new_location.name

                # Create updated line
                updated_line = (f"{loc_name}, {loc_desc}, "
                              f"west = {doors['west']}, "
                              f"north = {doors['north']}, "
                              f"east = {doors['east']}, "
                              f"south = {doors['south']}")
                updated_lines.append(updated_line)

        # Add the new location
        new_line = (f"{new_location.name}, {new_location.description}, "
                   f"west = {new_location.doors['west']}, "
                   f"north = {new_location.doors['north']}, "
                   f"east = {new_location.doors['east']}, "
                   f"south = {new_location.doors['south']}")
        updated_lines.append(new_line)

        # Write all locations back to CSV
        with open("locations.csv", "w") as file:
            file.write("\n".join(updated_lines) + "\n")

    def add_custom_creature(self):
        """Handle add custom creature"""
        # Get creature details with validation for blank fields
        nickname = input("Enter creature nickname: ").strip()
        if not nickname:
            print("Error: Creature nickname cannot be blank")
            return

        description = input("Enter creature description: ").strip()
        if not description:
            print("Error: Creature description cannot be blank")
            return

        adoptable = input("Is this creature adoptable (yes/no)?: ").strip().lower()
        if not adoptable or adoptable not in ["yes", "no"]:
            print("Error: Adoptable field must be either 'yes' or 'no'")
            return

        # Create the creature
        creature = (
            Pymon(nickname, description)
            if adoptable == "yes"
            else Animal(nickname, description)
        )

        # Add to record
        self.record.creatures.append(creature)

        # Read existing content
        try:
            with open("creatures.csv", "r") as file:
                lines = file.readlines()
                # Remove any empty lines at the end
                while lines and not lines[-1].strip():
                    lines.pop()
        except FileNotFoundError:
            lines = []

        # Write the new creature
        with open("creatures.csv", "a") as file:
            if lines and not lines[-1].endswith('\n'):
                file.write('\n')  # Add newline if the last line doesn't have one
            file.write(f"{nickname}, {description}, {adoptable}\n")
        
        print("Custom creature added successfully.")
