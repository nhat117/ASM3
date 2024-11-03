""""
Assignment: Pymon Game Assignment 3
Course: COSC2531 - Programming Fundamentals
Author: Thomas Bui
Student ID: s3878174
Highest Part Attempted: HD
"""

class InvalidDirectionException(Exception):
    """Exception raised for invalid directions."""

    def __init__(self, msg):
        msg = f"Invalid direction: {msg}, please choose from west, north, east, or south."
        super().__init__(msg)


class InvalidInputFileFormat(Exception):
    """Exception raised for invalid input file format."""

    def __init__(self, msg):
        msg = f"Invalid input file format: {msg}"
        super().__init__(msg)


class GameError(Exception):
    """Exception raised for game errors."""

    def __init__(self, msg):
        msg = f"Game error: {msg}"
        super().__init__(msg)


class AnimalCaptureError(Exception):
    """Exception raised when attempting to capture an Animal."""

    def __init__(self):
        msg = "Animals cannot be captured or added to the bench. Only Pymons can be captured in battle."
        super().__init__(msg)
