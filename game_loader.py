""""
Assignment: Pymon Game Assignment 3
Course: COSC2531 - Programming Fundamentals
Author: Thomas Bui
Student ID: s3878174
Highest Part Attempted: HD
"""

from operation import Operation
from record import Record
from creature import Pymon
import random


class GameLoader:
    __instance = None

    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern to ensure only one game instance."""
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        """Initialize the game state."""
        self.record = Record()

    def load_record(self, args):
        """Load record data based on the number of command-line arguments."""
        if len(args) == 1:
            self.record.load_data()
        elif len(args) == 2:
            self.record.load_data(locations_file=args[1])
        elif len(args) == 3:
            self.record.load_data(locations_file=args[1], creatures_file=args[2])
        elif len(args) == 4:
            self.record.load_data(
                locations_file=args[1],
                creatures_file=args[2],
                items_file=args[3],
            )
        else:
            print("Invalid number of arguments. Please provide up to 3 files.")

    def show_help(self):
        """Display help and usage instructions for the game."""
        usage = """
        Usage: pymon_game [locations_file] [creatures_file] [items_file]

        Options:
        --help              Show this usage information.

        Example:
        pymon_game                     Start the game with default settings.
        pymon_game locations.csv        Start the game with a custom locations file.
        pymon_game locations.csv creatures.csv items.csv    Start the game with custom locations, creatures, and items files.
        """
        print(usage)

    def start(self, args):
        """Start the game, load data, and initialize Pymon."""
        if "--help" in args:
            self.show_help()
            return

        self.load_record(args)

        pymon = Pymon(
            "Kimimon",
            "White and yellow Pymon with a square face",
            random.choice(self.record.locations),
        )

        operation = Operation(pymon, self.record)
        operation.menu()
