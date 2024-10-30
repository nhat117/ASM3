import sys
import random
import datetime

# Import the GameState class
from game_state import GameState
from location import Location
from creature import Pymon, Animal
from record import Record
from exceptions import InvalidDirectionException


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
                        loc_name = connected_loc.name if isinstance(connected_loc, Location) else connected_loc
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
            print(f"Location: {creature.location.name if creature.location else 'Unknown'}")
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
        if command == "1":
            self.pymon.inspect()
        elif command == "2":
            self.pymon.location.inspect()
        elif command == "3":
            direction = input("Moving to which direction?: ").lower()
            try:
                # Pass game_state to move method
                needs_switch = self.pymon.move(direction, self._game_state)
                if needs_switch:
                    # Force switch to a Pymon with energy
                    self.force_switch_pymon()
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
                captured_pymon = self.pymon.challenge(creature)
                if captured_pymon and isinstance(captured_pymon, Pymon):
                    # Add captured Pymon to bench with default energy
                    self._game_state.bench_pymons.append({
                        'nickname': captured_pymon.nickname,
                        'description': captured_pymon.description,
                        'inventory': [],  # Start with empty inventory
                        'stats': {
                            'energy': 3,  # Start with full energy
                            'has_immunity': False,
                            'move_count': 0,
                            'battle_stats': []
                        }
                    })
                    print(f"{captured_pymon.nickname} has been added to your bench!")
            else:
                print(f"There is no creature named {creature_name} here.")
        elif command == "7":
            self.pymon.display_battle_stats()
        elif command == "8":
            # Save game using Record's save_game_state method
            save_file = input("Enter save file name (default: save2024.csv): ").strip()
            if not save_file:
                save_file = 'save2024.csv'
            
            # Save game state with current Pymon
            self._record.save_game_state(save_file, self._pymon)
            print(f"Game progress saved to {save_file}")
            
        elif command == "9":
            # Load game using Record's load_game_state method
            save_file = input("Enter save file name to load (default: save2024.csv): ").strip()
            if not save_file:
                save_file = 'save2024.csv'
            
            try:
                # Load game state and get reconstructed Pymon
                loaded_pymon = self._record.load_game_state(save_file)
                if loaded_pymon:
                    self._pymon = loaded_pymon
                    # Get bench Pymons from game state
                    self._game_state = self._record._game_state
                    print(f"Game progress loaded from {save_file}")
                    self.generate_stats()
                else:
                    print("No valid saved game data found. Starting with current Pymon state.")
                    self.generate_stats()
            except Exception as e:
                print(f"Error loading game: {str(e)}")
                print("Starting with current Pymon state.")
                self.generate_stats()

        elif command == "10":
            self.add_custom_location()
        elif command == "11":
            self.add_custom_creature()
        elif command == "12":
            self.display_setup()
        elif command == "13":
            self.view_bench_pymons()
        elif command == "14":
            self.switch_active_pymon()
        elif command == "15":
            print("Exiting the program.")
            sys.exit(0)
        else:
            print("Invalid command, please try again.")

    def force_switch_pymon(self):
        """Force switch to a Pymon with energy when current Pymon runs out of energy."""
        while True:
            choice = input("Enter the number of the Pymon you want to switch to: ")
            try:
                index = int(choice) - 1
                if 0 <= index < len(self._game_state.bench_pymons):
                    selected_pymon = self._game_state.bench_pymons[index]
                    # Check if selected Pymon has energy
                    if 'stats' in selected_pymon and selected_pymon['stats'].get('energy', 0) > 0:
                        # Store current Pymon's data in bench
                        current_pymon_data = {
                            'nickname': self._pymon.nickname,
                            'description': self._pymon.description,
                            'inventory': [item.name for item in self._pymon.inventory],
                            'stats': {
                                'energy': self._pymon.energy,
                                'has_immunity': self._pymon.has_immunity,
                                'move_count': self._pymon.move_count,
                                'battle_stats': self._pymon.battle_stats
                            }
                        }
                        
                        # Create new Pymon instance
                        new_pymon = Pymon(
                            selected_pymon['nickname'],
                            selected_pymon['description'],
                            self._pymon.location
                        )
                        
                        # Set up new Pymon's stats and inventory
                        if 'stats' in selected_pymon:
                            new_pymon.energy = selected_pymon['stats'].get('energy', 3)
                            new_pymon.has_immunity = selected_pymon['stats'].get('has_immunity', False)
                            new_pymon.move_count = selected_pymon['stats'].get('move_count', 0)
                            new_pymon.battle_stats = selected_pymon['stats'].get('battle_stats', [])
                        
                        if selected_pymon.get('inventory'):
                            for item_name in selected_pymon['inventory']:
                                for location in self._record.locations:
                                    item = next((i for i in location.items if i.name == item_name), None)
                                    if item:
                                        new_pymon.inventory.append(item)
                                        location.items.remove(item)
                                        break
                        
                        # Update bench with current Pymon's data
                        self._game_state.bench_pymons[index] = current_pymon_data
                        
                        # Switch active Pymon
                        self._pymon = new_pymon
                        print(f"\nSwitched to {new_pymon.nickname}!")
                        print(f"Energy: {new_pymon.energy}/3")
                        return
                    else:
                        print("That Pymon has no energy! Choose another one.")
                else:
                    print("Invalid Pymon number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def view_bench_pymons(self):
        """Display all Pymons on the bench."""
        if not self._game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return
            
        print("\n=== Your Bench Pymons ===")
        for i, pymon in enumerate(self._game_state.bench_pymons, 1):
            print(f"\n{i}) {pymon['nickname']}")
            print(f"   Description: {pymon['description']}")
            if 'stats' in pymon:
                print(f"   Energy: {pymon['stats'].get('energy', 3)}/3")
            if pymon.get('inventory'):
                print(f"   Inventory: {', '.join(pymon['inventory'])}")

    def switch_active_pymon(self):
        """Switch the currently active Pymon with one from the bench."""
        if not self._game_state.bench_pymons:
            print("Your bench is empty. Capture some Pymons in battle!")
            return
            
        self.view_bench_pymons()
        choice = input("\nEnter the number of the Pymon you want to switch to (or press Enter to cancel): ")
        
        if not choice:
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(self._game_state.bench_pymons):
                # Get selected Pymon from bench
                selected_pymon = self._game_state.bench_pymons[index]
                
                # Store current Pymon's data in bench
                current_pymon_data = {
                    'nickname': self._pymon.nickname,
                    'description': self._pymon.description,
                    'inventory': [item.name for item in self._pymon.inventory],
                    'stats': {
                        'energy': self._pymon.energy,
                        'has_immunity': self._pymon.has_immunity,
                        'move_count': self._pymon.move_count,
                        'battle_stats': self._pymon.battle_stats
                    }
                }
                
                # Create new Pymon instance
                new_pymon = Pymon(
                    selected_pymon['nickname'],
                    selected_pymon['description'],
                    self._pymon.location
                )
                
                # Set up new Pymon's stats and inventory
                if 'stats' in selected_pymon:
                    new_pymon.energy = selected_pymon['stats'].get('energy', 3)
                    new_pymon.has_immunity = selected_pymon['stats'].get('has_immunity', False)
                    new_pymon.move_count = selected_pymon['stats'].get('move_count', 0)
                    new_pymon.battle_stats = selected_pymon['stats'].get('battle_stats', [])
                
                if selected_pymon.get('inventory'):
                    for item_name in selected_pymon['inventory']:
                        for location in self._record.locations:
                            item = next((i for i in location.items if i.name == item_name), None)
                            if item:
                                new_pymon.inventory.append(item)
                                location.items.remove(item)
                                break
                
                # Update bench with current Pymon's data
                self._game_state.bench_pymons[index] = current_pymon_data
                
                # Switch active Pymon
                self._pymon = new_pymon
                print(f"\nSwitched to {new_pymon.nickname}!")
                
                # Show current stats
                print(f"Energy: {new_pymon.energy}/3")
                if new_pymon.inventory:
                    print(f"Current inventory: {', '.join(item.name for item in new_pymon.inventory)}")
                else:
                    print("Current inventory is empty.")
            else:
                print("Invalid Pymon number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

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
        print(f"Location: {self.pymon.location.name if self.pymon.location else 'None'}")
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
