""""
Assignment: Pymon Game Assignment 3
Course: COSC2531 - Programming Fundamentals
Author: Thomas Bui
Student ID: s3878174
Highest Part Attempted: HD

# Design processs
### Modular Approach
I organized the game by dividing each feature into specific classes and methods. 
This modular structure improved organization, as each class and method manages a specific part of the game’s logic. 
For example, classes like `Location`, `Creature`, and `Pymon` each handle different aspects independently, making it easier to add new features in the future.

### Object-Oriented Programming (OOP) Principles

- **Encapsulation**: Each class includes its own data and methods, like location details and creature attributes, protecting them from direct changes.
- **Inheritance**: The `Pymon` class extends the `Creature` class to add attributes like energy and movement, which reduces redundancy by reusing the properties of `Creature`.
- **Polymorphism**: Methods such as `move()` and `challenge()` work differently in each subclass. 
- **Abstraction**: Complex game details, like tracking game progress, managing battles, and updating energy, are hidden in the class GameState.

### Singleton Pattern
I used a singleton pattern for the `Record` and `Operation` classes to keep a single instance managing game data and operations, which ensures consistency in the program.

### Private Attributes
Some classes use private attributes, which helps keep certain data secure by restricting access to only within the class. 
---

### **Reflection**:

This project was a valuable chance to apply modular design principles in game development.
I organized it into distinct classes and methods, like Location, Creature, and Pymon,
which kept things manageable and allowed easy feature expansion.
This approach also deepened my understanding of object-oriented programming (OOP) principles.
Encapsulation preserved data integrity, inheritance streamlined code reuse for Pymon, and polymorphism made behaviors flexible and polished.
Abstraction hid complex details from the player, enhancing the interface, while the Singleton pattern and private attributes maintained consistency and controlled access.

Starting with UML class diagrams helped visualize structure, keeping me aligned with project goals.
Despite these preparations, managing navigation, item usage, and energy interactions was challenging,
but with several iterations and testing, I successfully integrated these elements.

Looking forward, I see potential upgrades such as database integration, for better data handling
and expanded item functionality such as marketplace and trading.

References:
	1.	Python Documentation for the list copy method:
	•	W3Schools, “Python List copy() Method,” W3Schools.com. [Online]. Available: https://www.w3schools.com/python/ref_list_copy.asp. [Accessed: 03-Nov-2024]..
	2.	Stack Overflow discussion on reading CSV files without libraries:
	•	K. A. Roman, “Open and read a CSV file without libraries,” Stack Overflow, Oct. 2019. [Online]. Available: https://stackoverflow.com/questions/58572440/open-and-read-a-csv-file-without-libraries. [Accessed: 18-Oct-2024].
	3.	UML Class Diagram tutorial on Visual Paradigm:
	•	Visual Paradigm, “UML Class Diagram Tutorial,” Visual Paradigm Guide, [Online]. Available: https://www.visual-paradigm.com/guide/uml-unified-modeling-language/uml-class-diagram-tutorial/. [Accessed: 18-Oct-2024].
	4.	Stack Overflow discussion on Python shorthand for if-else:
	•	A. Paul, “Python if-else shorthand,” Stack Overflow, Jan. 2013. [Online]. Available: https://stackoverflow.com/questions/14461905/python-if-else-short-hand. [Accessed: 18-Oct-2024].
 	5.	Guide of how to use sys.argv
 	•	GeeksforGeeks, “How to use sys.argv in Python,” GeeksforGeeks.org. [Online]. Available: https://www.geeksforgeeks.org/how-to-use-sys-argv-in-python/. [Accessed: 03-Nov-2024].

The program have been divided into creature.py, exceptions.py, game_loader.py, game_state.py. location.py, operation.py, pymon_game.py, record.py and cannot work without any file missing

Known Issues:
- **None identified at the time of submission**: 

"""

from game_loader import GameLoader
import sys


def main():
    """Main function to start the game."""
    try:
        game = GameLoader()
        game.start(sys.argv)
    except Exception as e:
        print(f"An error occurred: {e}")


# Entry point of the game
if __name__ == "__main__":
    main()
