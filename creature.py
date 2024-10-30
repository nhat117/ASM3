# Creature class
from exceptions import *
import sys
import random
import datetime


class Creature:
    def __init__(self, nickname, description, location=None):
        self._nickname = nickname
        self._description = description
        self._location = location

    # Getter and setter for nickname
    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, new_nickname):
        self._nickname = new_nickname

    # Getter and setter for description
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

    # Getter and setter for location
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, new_location):
        self._location = new_location


# Pymon class (inherits Creature)
class Pymon(Creature):
    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)
        self._energy = 3
        self._inventory = []  # Pymon inventory to store items
        self._has_immunity = False
        self._move_count = 0
        self._battle_stats = []

    @property
    def battle_stats(self):
        return self._battle_stats

    @battle_stats.setter
    def battle_stats(self, new_stats):
        self._battle_stats = new_stats

    # Getter and setter for energy
    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, new_energy):
        if 0 <= new_energy <= 3:
            self._energy = new_energy
        else:
            raise ValueError("Energy must be between 0 and 3.")

    # Getter and setter for inventory
    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, new_inventory):
        if isinstance(new_inventory, list):
            self._inventory = new_inventory
        else:
            raise ValueError("Inventory must be a list.")

    # Getter and setter for has_immunity
    @property
    def has_immunity(self):
        return self._has_immunity

    @has_immunity.setter
    def has_immunity(self, new_immunity):
        if isinstance(new_immunity, bool):
            self._has_immunity = new_immunity
        else:
            raise ValueError("has_immunity must be a boolean value.")

    @property
    def move_count(self):
        return self._move_count

    @move_count.setter
    def move_count(self, new_move_count):
        self._move_count = new_move_count

    def pick_item(self, item):
        """Attempt to pick up an item."""
        if item.name.lower() == "tree":
            print("The tree is just for decoration and cannot be picked up.")
            return
            
        if item.can_be_picked:
            self.inventory.append(item)
            print(f"You picked up {item.name} from the ground!")
        else:
            print(f"The {item.name} cannot be picked up.")

    def view_inventory(self):
        """Display the items in the inventory and allow using an item."""
        if self.inventory:
            print(
                "You are carrying: " + ", ".join([item.name for item in self.inventory])
            )
            # Display in a list
            for index, item in enumerate(self.inventory, start=1):
                print(f"{index}) {item.name} - {item.description}")

            # Allow user to select an item to use
            item_choice = input("Select an item number to use or press Enter to skip: ")
            if item_choice.isdigit():
                item_index = int(item_choice) - 1
                if 0 <= item_index < len(self.inventory):
                    self.use_item(self.inventory[item_index])
                else:
                    print("Invalid item number.")
            elif item_choice:
                print("Invalid input.")
        else:
            print("You have no items.")

    def move(self, direction, game_state=None):
        """Move in the specified direction. Returns True if energy is depleted."""
        if direction in self.location.doors and self.location.doors[direction]:
            new_location = self.location.doors[direction]
            self.location = new_location
            print(f"You traveled {direction} and arrived at {new_location.name}.")
            # Debug: Print creatures in the new location
            print("Creatures in the new location:")
            for creature in new_location.creatures:
                print(f"- {creature.nickname}")

            # Decrease energy after every 2 moves
            self._move_count += 1
            if self._move_count % 2 == 0:
                self._energy -= 1
                print(
                    f"{self.nickname} lost 1 energy due to movement. Energy: {self._energy}/3"
                )
                if self._energy <= 0:
                    print(
                        f"{self.nickname} is out of energy and escaped into the wild!"
                    )
                    # Check if there are available Pymons on the bench
                    if game_state and game_state.bench_pymons:
                        available_pymons = []
                        print("\nAvailable Pymons on bench:")
                        for i, pymon in enumerate(game_state.bench_pymons, 1):
                            # Create temporary Pymon to check energy
                            temp_pymon = Pymon(pymon['nickname'], pymon['description'])
                            if 'stats' in pymon and 'energy' in pymon['stats']:
                                temp_pymon.energy = pymon['stats']['energy']
                            if temp_pymon.energy > 0:
                                available_pymons.append((i, pymon))
                                print(f"{i}) {pymon['nickname']} - Energy: {temp_pymon.energy}/3")
                        
                        if available_pymons:
                            print("\nYou must switch to a Pymon that still has energy!")
                            return True
                        else:
                            print("No Pymons with energy available. Game over.")
                            sys.exit(0)
                    else:
                        print("No backup Pymons available. Game over.")
                        sys.exit(0)
        else:
            raise InvalidDirectionException(f"There is no door to the {direction}.")
        return False

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self._energy}/3")

    def challenge(self, creature):
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        wins, losses, draws = 0, 0, 0
        had_immunity = self._has_immunity  # Store initial immunity state
        
        while wins < 2 and losses < 2 and self._energy > 0:
            player_choice = input("Your turn (r)ock, (p)aper, or (s)cissor?: ").lower()
            if player_choice not in ["r", "p", "s"]:
                print("Invalid choice, please choose r, p, or s.")
                continue
            opponent_choice = random.choice(["r", "p", "s"])
            print(f"Your opponent issued {opponent_choice}!")
            result = self.resolve_battle(player_choice, opponent_choice)
            if result == "win":
                wins += 1
                print(f"You won 1 encounter!")
            elif result == "lose":
                losses += 1
                if not self._has_immunity:
                    self._energy -= 1
                    print(
                        f"You lost 1 encounter and lost 1 energy. Energy: {self._energy}/3"
                    )
                else:
                    print(
                        f"You lost 1 encounter but your immunity protected you. Energy: {self._energy}/3"
                    )
                    self._has_immunity = False  # Remove immunity after it's used
            else:
                draws += 1

        # Remove magic potion from inventory after battle if immunity was used
        if had_immunity:
            for item in self._inventory[:]:  # Create a copy to safely modify during iteration
                if item.name.lower() == "magic potion":
                    self._inventory.remove(item)
                    break

        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M%p")
        self._battle_stats.append(
            {
                "timestamp": timestamp,
                "opponent": creature.nickname,
                "wins": wins,
                "draws": draws,
                "losses": losses,
            }
        )

        if wins == 2:
            print(
                f"Congrats! You won the battle and captured {creature.nickname}!"
            )
            # Remove the creature from its current location
            if creature.location and hasattr(creature.location, 'creatures'):
                creature.location.creatures.remove(creature)
            creature.location = None
            # Return the captured creature for adding to bench
            return creature
        else:
            print("You lost the battle!")
            return None

    def display_battle_stats(self):
        total_wins, total_draws, total_losses = 0, 0, 0
        print(f'Pymon Nickname: "{self.nickname}"')
        for i, stat in enumerate(self._battle_stats, start=1):
            print(
                f"Battle {i}, {stat['timestamp']} Opponent: \"{stat['opponent']}\", W: {stat['wins']} D: {stat['draws']} L: {stat['losses']}"
            )
            total_wins += stat["wins"]
            total_draws += stat["draws"]
            total_losses += stat["losses"]
        print(f"Total: W: {total_wins} D: {total_draws} L: {total_losses}")

    def resolve_battle(self, player_choice, opponent_choice):
        """Resolve the rock-paper-scissor battle."""
        outcomes = {
            ("r", "r"): "draw",
            ("r", "p"): "lose",
            ("r", "s"): "win",
            ("p", "r"): "win",
            ("p", "p"): "draw",
            ("p", "s"): "lose",
            ("s", "r"): "lose",
            ("s", "p"): "win",
            ("s", "s"): "draw",
        }
        return outcomes.get((player_choice, opponent_choice))

    def use_item(self, item):
        """Use an item from the inventory."""
        if not item:
            print("Invalid item.")
            return

        if item.name.lower() == "tree":
            print("Trees are just for decoration and cannot be used.")
            return

        if item.name.lower() == "apple":
            if self._energy < 3:
                self._energy = min(3, self._energy + 1)
                self._inventory.remove(item)
                print(f"{self.nickname} ate the apple. Energy: {self._energy}/3")
            else:
                print(f"{self.nickname} is already at full energy.")
        
        elif item.name.lower() == "magic potion":
            if not self._has_immunity:
                self._has_immunity = True
                print(f"{self.nickname} used the magic potion and is now immune for one battle.")
            else:
                print(f"{self.nickname} already has immunity active.")
        
        elif item.name.lower() == "binocular":
            direction = input("Use binocular to view (current/west/north/east/south): ").lower()
            
            if direction == "current":
                # Get current location details
                location_desc = []
                if self.location.creatures:
                    creatures = [c.nickname for c in self.location.creatures if c != self]
                    if creatures:
                        location_desc.append(", ".join(creatures))
                
                # Add connected locations
                for dir, loc in self.location.doors.items():
                    if loc:
                        location_desc.append(f"in the {dir} is {loc.name}")
                
                if location_desc:
                    print(", ".join(location_desc))
                else:
                    print("Nothing notable in the current location.")
            
            elif direction in ["west", "north", "east", "south"]:
                if direction in self.location.doors and self.location.doors[direction]:
                    connected_location = self.location.doors[direction]
                    items = [item.name for item in connected_location.items] if hasattr(connected_location, 'items') else []
                    if items:
                        print(f"In the {direction}, there seems to be {connected_location.name} with {', '.join(items)}")
                    else:
                        print(f"In the {direction}, there seems to be {connected_location.name}")
                else:
                    print("This direction leads nowhere")
            else:
                print("Invalid direction for binocular use.")
        else:
            print(f"{item.name} cannot be used.")


# Animal class (inherits Creature)
class Animal(Creature):
    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)

    def inspect(self):
        print(f"Animal {self.nickname}: {self.description}")
