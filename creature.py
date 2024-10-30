# Creature class
from exceptions import *
import sys
import random
import datetime
from item import MAX_ENERGY

THRESHOLD = 2  # Number of wins needed to capture a creature
LOSS_ENERGY_RATE = -1
WIN_THRESHOLD = 2


class Creature:
    def __init__(self, nickname, description, location=None):
        self._nickname = nickname
        self._description = description
        self._location = location

    @property
    def nickname(self):
        return self._nickname

    @nickname.setter
    def nickname(self, new_nickname):
        self._nickname = new_nickname

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description):
        self._description = new_description

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
        self._energy = MAX_ENERGY
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
        if 0 <= new_energy <= MAX_ENERGY:
            self._energy = new_energy
        else:
            # Instead of raising an error, clamp the value
            self._energy = max(0, min(new_energy, MAX_ENERGY))

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
            self.location = self.location.doors[direction]
            self.display_new_location()

            self.move_count += 1
            if self.move_count % 2 == 0:
                self.decrease_energy()

            if self.energy <= 0:
                self.handle_energy_depletion(game_state)
                return True
        else:
            raise InvalidDirectionException(f"There is no door to the {direction}.")

        return False

    def display_new_location(self):
        """Display information about the new location after moving."""
        print(f"You traveled and arrived at {self.location.name}.")
        print("Creatures in the new location:")
        for creature in self.location.creatures:
            print(f"- {creature.nickname}")

    def decrease_energy(self):
        """Decrease Pymon's energy after every 2 moves and display the status."""
        self.energy = self.energy - 1
        print(
            f"{self.nickname} lost 1 energy due to movement. Energy: {self._energy}/{MAX_ENERGY}"
        )

    def handle_energy_depletion(self, game_state):
        """Handle the situation when the Pymon is out of energy."""
        print(f"{self.nickname} is out of energy and escaped into the wild!")
        if game_state and game_state.bench_pymons:
            available_pymons = self.get_available_pymons(game_state.bench_pymons)
            if available_pymons:
                print("\nYou must switch to a Pymon that still has energy!")
            else:
                self.end_game()
        else:
            self.end_game()

    def get_available_pymons(self, bench_pymons):
        """Check and display Pymons on the bench that still have energy."""
        available_pymons = []
        print("\nAvailable Pymons on bench:")
        for i, pymon in enumerate(bench_pymons, 1):
            temp_pymon = self.create_temp_pymon(pymon)
            if temp_pymon.energy > 0:
                available_pymons.append((i, pymon))
                print(f"{i}) {pymon['nickname']} - Energy: {temp_pymon.energy}/3")
        return available_pymons

    def create_temp_pymon(self, pymon_data):
        """Create a temporary Pymon to check its energy."""
        temp_pymon = Pymon(pymon_data["nickname"], pymon_data["description"])
        if "stats" in pymon_data and "energy" in pymon_data["stats"]:
            temp_pymon.energy = pymon_data["stats"]["energy"]
        return temp_pymon

    def end_game(self):
        """End the game if no Pymons with energy are available."""
        print("No Pymons with energy available. Game over.")
        sys.exit(0)

    def inspect(self):
        print(f"Pymon {self.nickname}: {self.description}, Energy: {self._energy}/{MAX_ENERGY}")

    def challenge(self, creature):
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        wins, losses, draws = 0, 0, 0
        had_immunity = self._has_immunity  # Store initial immunity state

        while wins < THRESHOLD and losses < THRESHOLD and self._energy > 0:
            player_choice = self.get_player_choice()
            if not player_choice:
                continue
            opponent_choice = self.get_move_opponent()
            print(f"Your opponent issued {opponent_choice}!")

            result = self.resolve_battle(player_choice, opponent_choice)
            wins, losses = self.update_battle_results(result, wins, losses)

        self.handle_immunity_removal(had_immunity)

        self.generate_stats(creature, wins, draws, losses)

        return self.handle_outcome(creature, wins)

    def get_player_choice(self):
        """Prompt the player to choose rock, paper, or scissors."""
        player_choice = input("Your turn (r)ock, (p)aper, or (s)cissor?: ").lower()
        if player_choice not in ["r", "p", "s"]:
            print("Invalid choice, please choose r, p, or s.")
            return None
        return player_choice

    def get_move_opponent(self):
        """Get a random choice for the opponent."""
        return random.choice(["r", "p", "s"])

    def update_battle_results(self, res, wins, lose):
        """Update the win/loss counters based on the battle result."""
        if res == "win":
            wins += 1
            print(f"You won 1 encounter!")
        elif res == "lose":
            lose += 1
            self.handle_player_lose()
        return wins, lose

    def handle_player_lose(self):
        """Handle the case where the player loses an encounter."""
        if not self.has_immunity:
            self.energy = self.energy + LOSS_ENERGY_RATE  # Use energy setter
            print(
                f"You lost 1 encounter and lost 1 energy. Energy: {self._energy}/{MAX_ENERGY}"
            )
        else:
            print(
                f"You lost 1 encounter but your immunity protected you. Energy: {self._energy}/{MAX_ENERGY}"
            )
            self.has_immunity = False  # Remove immunity after it's used

    def handle_immunity_removal(self, had_immunity):
        """Remove the magic potion from inventory if immunity was used."""
        if had_immunity:
            for item in self.inventory[
                        :
                        ]:  # Create a copy to safely modify during iteration
                if item.name.lower() == "magic potion":
                    self.inventory.remove(item)
                    break

    def generate_stats(self, creature, wins, draws, losses):
        """Record the battle statistics with a timestamp."""
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M%p")
        self.battle_stats.append(
            {
                "timestamp": timestamp,
                "opponent": creature.nickname,
                "wins": wins,
                "draws": draws,
                "losses": losses,
            }
        )

    def handle_outcome(self, creature, wins):
        if wins == WIN_THRESHOLD:
            print(f"Congrats! You won the battle and captured {creature.nickname}!")
            self.capture_creature(creature)
            return creature
        else:
            print("You lost the battle!")
            return None

    def capture_creature(self, creature):
        """Remove the captured creature from its location and set its location to None."""
        if creature.location and hasattr(creature.location, "creatures"):
            creature.location.creatures.remove(creature)
        creature.location = None

    def display_battle_stats(self):
        """Get and display the battle statistics for the Pymon."""
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

        item_name = item.name.lower()

        if item_name == "tree":
            self.use_tree(item)
        elif item_name == "apple":
            self.use_apple(item)
        elif item_name == "magic potion":
            self.use_magic_potion(item)
        elif item_name == "binocular":
            self.use_binocular()
        else:
            print(f"{item.name} cannot be used.")

    def use_tree(self, item):
        """Handle the case where a tree item is attempted to be used."""
        print("Trees are just for decoration and cannot be used.")

    def use_apple(self, item):
        """Handle the case where an apple item is used."""
        if self._energy < 3:
            self._energy = min(3, self._energy + 1)
            self._inventory.remove(item)
            print(f"{self.nickname} ate the apple. Energy: {self._energy}/3")
        else:
            print(f"{self.nickname} is already at full energy.")

    def use_magic_potion(self, item):
        """Handle the case where a magic potion is used."""
        if not self._has_immunity:
            self._has_immunity = True
            print(
                f"{self.nickname} used the magic potion and is now immune for one battle."
            )
        else:
            print(f"{self.nickname} already has immunity active.")

    def use_binocular(self):
        """Handle the case where binoculars are used."""
        direction = input(
            "Use binocular to view (current/west/north/east/south): "
        ).lower()

        if direction == "current":
            self.view_curr_loc()
        elif direction in ["west", "north", "east", "south"]:
            self.view_connected_loc(direction)
        else:
            print("Invalid direction for binocular use.")

    def view_curr_loc(self):
        """Display information about the current location."""
        location_description = []
        if self.location.creatures:
            creatures = [c.nickname for c in self.location.creatures if c != self]
            if creatures:
                location_description.append(", ".join(creatures))

        for dir, loc in self.location.doors.items():
            if loc:
                location_description.append(f"in the {dir} is {loc.name}")

        if location_description:
            print(", ".join(location_description))
        else:
            print("Nothing notable in the current location.")

    def view_connected_loc(self, direction):
        """Display information about a connected location in a given direction."""
        if direction in self.location.doors and self.location.doors[direction]:
            connected_location = self.location.doors[direction]
            items = (
                [item.name for item in connected_location.items]
                if hasattr(connected_location, "items")
                else []
            )
            if items:
                print(
                    f"In the {direction}, there seems to be {connected_location.name} with {', '.join(items)}"
                )
            else:
                print(
                    f"In the {direction}, there seems to be {connected_location.name}"
                )
        else:
            print("This direction leads nowhere")


# Animal class (inherits Creature)
class Animal(Creature):
    """Class representing an animal in the game. An nimal cannot be pickup or used in battle."""

    def __init__(self, nickname, description, location=None):
        super().__init__(nickname, description, location)

    def inspect(self):
        """Inspect the animal and display its details."""
        print(f"Animal {self.nickname}: {self.description}")
