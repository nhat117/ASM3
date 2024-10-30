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
            # Save game using Record's save_game_state method
            save_file = input("Enter save file name (default: save2024.csv): ").strip()
            if not save_file:
                save_file = 'save2024.csv'
            
            # Update user pymon state before saving
            self._game_state.user_pymon = {
                'nickname': self._pymon.nickname,
                'description': self._pymon.description,
                'location': self._pymon.location.name if self._pymon.location else 'None',
                'stats': {
                    'energy': self._pymon.energy,
                    'has_immunity': self._pymon.has_immunity,
                    'move_count': self._pymon.move_count,
                    'battle_stats': self._pymon.battle_stats
                },
                'inventory': [item.name for item in self._pymon.inventory]
            }
            
            self._record.save_game_state(save_file)
            print(f"Game progress saved to {save_file}")
            
        elif command == "9":
            # Load game using Record's load_game_state method
            save_file = input("Enter save file name to load (default: save2024.csv): ").strip()
            if not save_file:
                save_file = 'save2024.csv'
            
            try:
                self._record.load_game_state(save_file)
                
                # Restore user pymon state
                user_data = self._game_state.user_pymon
                if user_data and isinstance(user_data, dict):
                    # Update pymon attributes if they exist in saved data
                    if 'nickname' in user_data and user_data['nickname']:
                        self._pymon.nickname = user_data['nickname']
                    if 'description' in user_data and user_data['description']:
                        self._pymon.description = user_data['description']
                    
                    # Find and set location
                    if 'location' in user_data and user_data['location'] != 'None':
                        for location in self._record.locations:
                            if location.name == user_data['location']:
                                self._pymon.location = location
                                break
                    
                    # Restore stats if they exist
                    if 'stats' in user_data and isinstance(user_data['stats'], dict):
                        stats = user_data['stats']
                        if 'energy' in stats:
                            self._pymon.energy = stats['energy']
                        if 'has_immunity' in stats:
                            self._pymon.has_immunity = stats['has_immunity']
                        if 'move_count' in stats:
                            self._pymon.move_count = stats['move_count']
                        if 'battle_stats' in stats:
                            self._pymon.battle_stats = stats['battle_stats']
                    
                    # Restore inventory if it exists
                    if 'inventory' in user_data:
                        self._pymon.inventory = []
                        for item_name in user_data['inventory']:
                            # Find the item in locations and add to inventory
                            for location in self._record.locations:
                                item = next((i for i in location.items if i.name == item_name), None)
                                if item:
                                    self._pymon.inventory.append(item)
                                    location.items.remove(item)
                                    break
                    
                    print(f"Game progress loaded from {save_file}")
                    self.generate_stats()  # Show current state after loading
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
