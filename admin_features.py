from hello import Creature, Pymon

def add_custom_creature():
    nickname = input("Enter creature nickname: ")
    description = input("Enter creature description: ")
    adoptable = input("Is this creature adoptable (yes/no)?: ").lower()

    # Determine the type of creature
    creature = Pymon(nickname, description) if adoptable == "yes" else Creature(nickname, description)

    # Save the creature to creatures.csv
    with open("creatures.csv", "a+") as file:
        file.seek(0, 2)  # Move the cursor to the end of the file
        if file.tell() > 0:  # Check if the file is not empty
            file.seek(file.tell() - 1)  # Move the cursor to the last character
            last_char = file.read(1)
            if last_char != "\n":
                file.write("\n")  # Add a newline if the last character is not a newline
        file.write(f"{nickname}, {description}, {adoptable}\n")
    
    print(f"Custom creature '{nickname}' added successfully.")

# Example usage
if __name__ == "__main__":
    add_custom_creature()
