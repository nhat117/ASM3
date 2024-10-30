import sys
import random
import datetime

class InvalidDirectionException(Exception):
    """Exception raised for invalid directions."""
    def __init__(self, message):
        message = f"Invalid direction: {message}, please choose from west, north, east, or south."
        super().__init__(message)


class InvalidInputFileFormat(Exception):
    """Exception raised for invalid input file format."""
    def __init__(self, message):
        message = f"Invalid input file format: {message}"
        super().__init__(message)


class GameError(Exception):
    """Exception raised for game errors."""
    def __init__(self, message):
        message = f"Game error: {message}"
        super().__init__(message)

class AnimalCaptureError(Exception):
    """Exception raised when attempting to capture an Animal."""
    def __init__(self):
        message = "Animals cannot be captured or added to the bench. Only Pymons can be captured in battle."
        super().__init__(message)
