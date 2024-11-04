from exceptions import InvalidDirectionException, AnimalCaptureError, GameError
import sys
import random
import datetime
from item import MAX_ENERGY

THRESHOLD = 2  # Number of wins needed to capture a creature
LOSS_ENERGY_RATE = -1
WIN_THRESHOLD = 2


class Creature:
    def __init__(self, nickname, desc, loc=None):
        self.__nickname = nickname
        self.__desc = desc
        self.__loc = loc

    @property
    def nickname(self):
        return self.__nickname

    @nickname.setter
    def nickname(self, new_nickname):
        self.__nickname = new_nickname

    @property
    def desc(self):
        return self.__desc

    @desc.setter
    def desc(self, new_description):
        self.__desc = new_description

    @property
    def loc(self):
        return self.__loc

    @loc.setter
    def loc(self, new_location):
        self.__loc = new_location


# Pymon class (inherits Creature)
class Pymon(Creature):
    def __init__(self, nickname, desc, loc=None):
        super().__init__(nickname, desc, loc)
        # Predefine all attributes in __init__
        self.__energy = MAX_ENERGY
        self.__inventory = []  # Pymon inventory to store items
        self.__has_immunity = False
        self.__move_count = 0
        self.__battle_stats = []
        self.__wins = 0
        self.__losses = 0
        self.__draws = 0
        self.__current_battle_opponent = None
        self.__last_battle_timestamp = None

    @property
    def battle_stats(self):
        return self.__battle_stats

    @battle_stats.setter
    def battle_stats(self, new_stats):
        self.__battle_stats = new_stats

    @property
    def energy(self):
        return self.__energy

    @energy.setter
    def energy(self, new_energy):
        if 0 <= new_energy <= MAX_ENERGY:
            self.__energy = new_energy
        else:
            # Instead of raising an error, clamp the value
            self.__energy = max(0, min(new_energy, MAX_ENERGY))

    @property
    def inventory(self):
        return self.__inventory

    @inventory.setter
    def inventory(self, new_inventory):
        if isinstance(new_inventory, list):
            self.__inventory = new_inventory
        else:
            raise ValueError("Inventory must be a list.")

    @property
    def has_immunity(self):
        return self.__has_immunity

    @has_immunity.setter
    def has_immunity(self, new_immunity):
        if isinstance(new_immunity, bool):
            self.__has_immunity = new_immunity
        else:
            raise ValueError("has_immunity must be a boolean value.")

    @property
    def move_count(self):
        return self.__move_count

    @move_count.setter
    def move_count(self, new_move_count):
        self.__move_count = new_move_count

    def pick_item(self, item):
        """Attempt to pick up an item."""
        if item.name.lower() == "tree":
            print("The tree is just for decoration and cannot be picked up.")
            return

        if item.is_pickable:
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
                print(f"{index}) {item.name} - {item.desc}")

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
        doors_dict = self.loc.doors.to_dict()
        if direction in doors_dict and doors_dict[direction]:
            self.loc = doors_dict[direction]
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
        print(f"You traveled and arrived at {self.loc.name}.")
        print("Creatures in the new location:")
        for creature in self.loc.creatures:
            print(f"- {creature.nickname}")

    def decrease_energy(self):
        """Decrease Pymon's energy after every 2 moves and display the status."""
        self.energy = self.energy - 1
        print(
            f"{self.nickname} lost 1 energy due to movement. Energy: {self.__energy}/{MAX_ENERGY}"
        )

    def handle_energy_depletion(self, game_state):
        """Handle the situation when the Pymon is out of energy."""
        print(f"{self.nickname} is out of energy and escaped into the wild!")

        # Remove the Pymon from the bench
        if game_state and game_state.bench_pymons:
            # Find and remove the current Pymon from the bench
            for i, pymon in enumerate(game_state.bench_pymons):
                if pymon["nickname"] == self.nickname:
                    game_state.bench_pymons.pop(i)
                    break

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
        print(f"Pymon {self.nickname}: {self.desc}, Energy: {self.energy}/{MAX_ENERGY}")

    def challenge(self, creature):
        print(f"{creature.nickname} gladly accepted your challenge! Ready for battle!")
        self.__wins, self.__losses, self.__draws = 0, 0, 0
        had_immunity = self.__has_immunity  # Store initial immunity state
        self.__current_battle_opponent = creature.nickname

        while self.energy > 0:
            if self.__wins >= THRESHOLD or self.__losses >= THRESHOLD:
                break

            player_choice = self.get_player_choice()
            if not player_choice:
                continue

            opponent_choice = self.get_move_opponent()
            print(f"Your opponent issued {opponent_choice}!")

            result = self.battle_judge(player_choice, opponent_choice)
            self.update_battle_results(result)

        self.handle_immunity_removal(had_immunity)
        self.__last_battle_timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M%p")
        self.generate_stats()

        return self.handle_outcome(creature)

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

    def update_battle_results(self, res):
        """Update the win/loss counters based on the battle result."""
        if res == "win":
            self.__wins += 1
            print(f"You won 1 encounter!")
        elif res == "lose":
            self.__losses += 1
            self.handle_player_lose()
        else:
            self.__draws += 1

    def handle_player_lose(self):
        """Handle the case where the player loses an encounter."""
        if not self.has_immunity:
            self.energy = self.energy + LOSS_ENERGY_RATE  # Use energy setter
            print(
                f"You lost 1 encounter and lost 1 energy. Energy: {self.__energy}/{MAX_ENERGY}"
            )
        else:
            print(
                f"You lost 1 encounter but your immunity protected you. Energy: {self.__energy}/{MAX_ENERGY}"
            )
            self.has_immunity = False  # Remove immunity after it's used

    def handle_immunity_removal(self, had_immunity):
        """Remove the magic potion from inventory if immunity was used."""
        if had_immunity:
            for item in self.inventory.copy():  # Avoid modifying inventory directly
                if item.name.lower() == "magic potion":
                    self.inventory.remove(item)
                    break

    def generate_stats(self):
        """Record the battle statistics with a timestamp."""
        self.battle_stats.append(
            {
                "timestamp": self.__last_battle_timestamp,
                "opponent": self.__current_battle_opponent,
                "wins": self.__wins,
                "draws": self.__draws,
                "losses": self.__losses,
            }
        )

    def handle_outcome(self, creature):
        if self.__wins == WIN_THRESHOLD:
            print(f"Congrats! You won the battle and captured {creature.nickname}!")
            self.capture(creature)
            return creature
        else:
            print("You lost the battle!")
            return None

    def capture(self, creature):
        """Remove the captured creature from its location and set its location to None."""
        if creature.loc and hasattr(creature.loc, "creatures"):
            creature.loc.creatures.remove(creature)
        creature.loc = None

    def display_battle_stats(self):
        """Get and display the battle statistics for the Pymon."""
        total_w, total_d, total_l = 0, 0, 0
        print(f'Pymon Nickname: "{self.nickname}"')
        for i, stat in enumerate(self.__battle_stats, start=1):
            print(
                f"Battle {i}, {stat['timestamp']} Opponent: \"{stat['opponent']}\", W: {stat['wins']} D: {stat['draws']} L: {stat['losses']}"
            )
            total_w += stat["wins"]
            total_d += stat["draws"]
            total_l += stat["losses"]
        print(f"Total: W: {total_w} D: {total_d} L: {total_l}")

    def battle_judge(self, player_choice, opponent_choice):
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
            self.use_magic_potion()
        elif item_name == "binocular":
            self.use_binocular()
        else:
            print(f"{item.name} cannot be used.")

    def use_tree(self, item):
        """Handle the case where a tree item is attempted to be used."""
        print("Trees are just for decoration and cannot be used.")

    def use_apple(self, item):
        """Handle the case where an apple item is used."""
        if self.__energy < 3:
            self.__energy = min(3, self.__energy + 1)
            self.__inventory.remove(item)
            print(f"{self.nickname} ate the apple. Energy: {self.__energy}/3")
        else:
            print(f"{self.nickname} is already at full energy.")

    def use_magic_potion(self):
        """Handle the case where a magic potion is used."""
        if not self.has_immunity:
            self.has_immunity = True
            print(
                f"{self.nickname} used the magic potion and is now immune for one battle."
            )
        else:
            print(
                f"{self.nickname} already has immunity active. Potion cannot be used."
            )

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
        loc_desc = []
        if self.loc.creatures:
            creatures = []
            for c in self.loc.creatures:
                if c != self:
                    creatures.append(c.nickname)
            if creatures:
                loc_desc.append(", ".join(creatures))

        doors_dict = self.loc.doors.to_dict()
        for direction, loc in doors_dict.items():
            if loc:
                loc_desc.append(f"in the {direction} is {loc.name}")

        if loc_desc:
            print(", ".join(loc_desc))
        else:
            print(" in the current location.")

    def view_connected_loc(self, direction):
        """Display information about a connected location in a given direction."""
        doors_dict = self.loc.doors.to_dict()
        if direction in doors_dict and doors_dict[direction]:
            connected_loc = doors_dict[direction]
            items = (
                [item.name for item in connected_loc.items]
                if hasattr(connected_loc, "items")
                else []
            )
            if items:
                print(
                    f"In the {direction}, there seems to be {connected_loc.name} with {', '.join(items)}"
                )
            else:
                print(f"In the {direction}, there seems to be {connected_loc.name}")
        else:
            print("This direction leads nowhere")


# Animal class (inherits Creature)
class Animal(Creature):
    """Class representing an animal in the game. An nimal cannot be pickup or used in battle."""

    def __init__(self, nickname, desc, loc=None):
        super().__init__(nickname, desc, loc)

    def inspect(self):
        """Inspect the animal and display its details."""
        print(f"Animal {self.nickname}: {self.desc}")
