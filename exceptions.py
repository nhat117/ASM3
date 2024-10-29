import sys
import random
import datetime

class InvalidDirectionException(Exception):
    def __init__(self, message):
        message = f"Invalid direction: {message}, please choose from west, north, east, or south."
        super().__init__(message)


class InvalidInputFileFormat(Exception):
    def __init__(self, message):
        message = f"Invalid input file format: {message}"
        super().__init__(message)


class GameError(Exception):
    def __init__(self, message):
        message = f"Game error: {message}"
        super().__init__(message)
        
