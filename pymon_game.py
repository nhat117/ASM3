""""
Assignment: Pymon Game Assignment 3
Course: COSC2531 - Programming Fundamentals
Author: Thomas Bui
Student ID: s3878174
Highest Part Attempted: HD

### **Design Process**:

- **Modular Approach**: I built the system by dividing tasks into separate functions and classes. This approach made it easier to work on specific parts of the program and made it more manageable. Each function handles one task, which improves both readability and maintenance. For example, classes like `Guest` and `Order` are independent, and this helps keep things organized.

- **Object-Oriented Programming (OOP) Principles**:
   - *Encapsulation*: Each class has its own data and methods. This keeps data safe inside the class, and outside parts of the program cannot change it directly.
   - *Inheritance*: I used inheritance to create subclasses like `ApartmentUnit` and `SupplementaryItem`. This helps reuse code and reduces duplication.
   - *Polymorphism*: The same method, like `display_info`, behaves differently depending on the type of product, whether it’s an apartment or a supplementary item. This flexibility helps manage different products easily.
   - *Abstraction*: The system hides complex parts of the code and only shows what’s necessary to the user, which simplifies how users interact with the program.

- **Singleton**: I used a singleton pattern for the `Records` and Operation class to ensure there is only one instance of the class. This helps manage data consistency and avoids creating multiple instances that could lead to conflicts.

- **Protected Attribute**: I used it to ensuring encapsulation while maintaining flexibility. This discourages external access to internal logic and helps avoid conflicts in subclass inheritance.

- **Input Validation**: To avoid mistakes, I implemented checks for user input. For example, the program ensures the correct number of guests is entered, and the booking dates are valid. This improves the reliability of the system and avoids problems during execution.

- **Error Handling and Custom Exceptions**: I created custom error messages, like `InvalidGuestNameError`, to manage mistakes such as invalid names or incorrect product details. This way, the program doesn’t crash when users make mistakes, and they can easily fix their input.

- **File Handling**: The program uses CSV files to store data about guests, products, and orders. This allows the system to save and load information between sessions, making it more practical. If a file is missing or corrupted, the program shows a clear error message without crashing.

- **Challenges**: The most difficult part was ensuring all the components, like bookings and supplementary items, worked well together. I had to design the system in a way that allowed different parts to interact smoothly. Another challenge was managing reward points and discounts accurately.

- **Refinement Process**: I improved the system step by step, making it more user-friendly. For example, I worked on how the user interacts with the program to ensure everything runs smoothly, and I simplified some parts of the code to avoid confusion.

---

### **Reflection**:

- **Learning Experience**: This assignment gave me the chance to practice using OOP concepts in a real-world scenario. By using classes and breaking the program into modules, I found it easier to develop, test, and maintain. It also helped me learn how to manage errors and work with files in Python.

- **Challenges**: The hardest part was making sure all the different parts worked together correctly. Handling reward points, supplementary items, and keeping the system organized was challenging, but it taught me a lot about planning and designing a system.

- **Improvements**: In the future, I think using a database instead of CSV files could make the system run more efficiently, especially if there are more records. It would also help with handling more complex booking scenarios, such as recurring bookings or long stays. I would also work on improving how the system handles dates to make it easier for users.

- **Overall Outcome**: The final system meets the assignment requirements and is user-friendly. It follows good programming practices and should be easy to update or expand in the future.

References:
For general principles on making code maintainable, readable, and clean, applicable to Python.
1. B. Slatkin, *Effective Python: 59 Specific Ways to Write Better Python*. San Francisco, CA: Pearson Education, 2015. [Online]. Available: [https://effectivepython.com/](https://effectivepython.com/). [Accessed: 18-Oct-2024].
For general principles on making code maintainable, readable, and clean, applicable to Python.
2. R. C. Martin, *Clean Code: A Handbook of Agile Software Craftsmanship*. Upper Saddle River, NJ: Pearson Education, 2008. [Online]. Available: [https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000001570/9780132350884](https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000001570/9780132350884). [Accessed: 18-Oct-2024].
For understanding the four pillars of OOP—encapsulation, inheritance, abstraction, and polymorphism—in a practical context.
3. B. A. Miles and D. McCullough, *Head First Object-Oriented Analysis and Design*. Sebastopol, CA: O'Reilly Media, 2006. [Online]. Available: [https://www.oreilly.com/library/view/head-first-object/0596008678/](https://www.oreilly.com/library/view/head-first-object/0596008678/). [Accessed: 18-Oct-2024].
For learning Python basics and error handling,
4. E. Matthes, *Python Crash Course: A Hands-On, Project-Based Introduction to Programming*, 2nd ed. San Francisco, CA: No Starch Press, 2019. [Online]. Available: [https://nostarch.com/pythoncrashcourse2e](https://nostarch.com/pythoncrashcourse2e). [Accessed: 18-Oct-2024].
For learning Python basics and error handling
5. L. Hu, "Exception Handling in Python," *Real Python*, Jun. 2019. [Online]. Available: [https://realpython.com/python-exceptions/](https://realpython.com/python-exceptions/). [Accessed: 18-Oct-2024].
For guidelines on writing clear and consistent docstrings in Python, ensuring the code adheres to standard documentation practices.
6. G. van Rossum and J. J. Lee, "PEP 257 – Docstring Conventions," *Python.org*. [Online]. Available: [https://www.python.org/dev/peps/pep-0257/](https://www.python.org/dev/peps/pep-0257/). [Accessed: 18-Oct-2024].

Compatability:
- **Python Version**: 3.10 and above due to the use of match case statements.

Assumption:
- **The system assumes all of the datafile are cleaned and correct.**

Known Issues:
- **None identified at the time of submission**: The program has been tested thoroughly, but additional testing may reveal areas that could be improved.
- **Format in display booking history function
- **Car park ID have to be change manually in the system
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
