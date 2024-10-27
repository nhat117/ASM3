import sys

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

    def inspect(self):
        print(f"You are at {self.name}. {self.description}")
        if self.creatures:
            for creature in self.creatures:
                print(f"Creature present: {creature.nickname} - {creature.description}")
        else:
            print("No creatures here.")

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

    def move(self, direction):
        if direction in self.location.doors and self.location.doors[direction]:
            new_location = self.location.doors[direction]
            self.location = new_location
            print(f"You traveled {direction} and arrived at {new_location.get_name()}.")
        else:
            print(f"There is no door to the {direction}. Pymon remains at its current location.")

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self.energy}/3")

# Record class
class Record:
    def __init__(self):
        self.locations = []
        self.creatures = []

    def load_data(self, locations_file, creatures_file):
        """Load data from CSV files (locations.csv and creatures.csv)."""
        # Sample data loading (replace with actual file reading)
        self.locations = [
            Location("Playground", "A place to play and have fun."),
            Location("School", "A secondary school for local creatures."),
            Location("Beach", "A sunny place with soft sand.")
        ]
        self.creatures = [
            Creature("Large Pymon", "White and blue large Pymon", self.locations[0]),
            Creature("Small Pymon", "Yellow and orange small Pymon", self.locations[1])
        ]
        self.locations[0].add_creature(self.creatures[0])
        self.locations[1].add_creature(self.creatures[1])

# Operation class
class Operation:
    def __init__(self, pymon, record):
        self.pymon = pymon
        self.record = record

    def menu(self):
        """Provide options for the player to choose."""
        while True:
            print("\nPlease issue a command to your Pymon:")
            print("1) Inspect Pymon")
            print("2) Inspect current location")
            print("3) Move")
            print("4) Exit the program")
            command = input("Your command: ")

            if command == "1":
                self.pymon.inspect()
            elif command == "2":
                self.pymon.location.inspect()
            elif command == "3":
                direction = input("Moving to which direction?: ").lower()
                self.pymon.move(direction)
            elif command == "4":
                print("Exiting the program.")
                sys.exit(0)
            else:
                print("Invalid command, please try again.")

# Main function to run the game
if __name__ == "__main__":
    # Setup locations, creatures, and Pymon
    record = Record()
    record.load_data('locations.csv', 'creatures.csv')

    # Place the Pymon in the playground initially
    pymon = Pymon("Kimimon", "White and yellow Pymon with a square face", record.locations[0])

    # Connect locations
    record.locations[0].connect("north", record.locations[2])  # Playground -> Beach
    record.locations[0].connect("west", record.locations[1])   # Playground -> School

    # Start the game
    operation = Operation(pymon, record)
    operation.menu()