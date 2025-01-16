# Pokémon Game in Python

## Overview
Welcome to the **Pokémon Game**, a command-line adventure game written in Python. In this game, players can explore a virtual world, capture Pokémon, train them, and battle against other trainers or wild Pokémon. This project is inspired by the popular Pokémon franchise and aims to provide a fun and interactive gaming experience.

---

## Features
- **Pokémon Capture**: Encounter and capture wild Pokémon.
- **Trainer Battles**: Challenge NPC trainers to Pokémon battles.
- **Leveling System**: Train your Pokémon to level up and learn new moves.
- **Turn-Based Combat**: Engage in strategic, turn-based Pokémon battles.
- **Inventory Management**: Use items like Poké Balls and potions during gameplay.

---

## Installation

### Prerequisites
- Python 3.8 or higher

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/pokemon-game.git
    ```
2. Navigate to the project directory:
    ```bash
    cd pokemon-game
    ```
3. Install dependencies (if any):
    ```bash
    pip install -r requirements.txt
    ```
4. Run the game:
    ```bash
    python pymon_game.py
    ```

---

## How to Play

1. **Start the Game**:
   Run the game using the command `python pymon_game.py` and follow the on-screen instructions.

2. **Catch Pokémon**:
   When encountering wild Pokémon, choose the option to throw a Poké Ball and attempt to capture it.

3. **Train Pokémon**:
   Battle against wild Pokémon or trainers to gain experience points (XP) and level up your team.

4. **Use Items**:
   Manage your inventory to use items like potions to heal your Pokémon or Poké Balls to catch new ones.

5. **Battle**:
   Select attacks strategically during battles to defeat opponents.

---

## Code Structure

- `pymon_game.py`: Entry point of the game.
- `creature.py`: Defines Pokémon classes, stats, and moves.
- `game_loader.py`: Loads game data from CSV files (e.g., creatures, items, locations).
- `game_state.py`: Manages the current state of the game, including player progress.
- `item.py`: Handles item-related functionality.
- `location.py`: Manages locations and exploration logic.
- `operation.py`: Contains utility functions for various game operations.
- `record.py`: Handles player save and load functionality.
- `exceptions.py`: Defines custom exceptions for better error handling.
- `class_diagram.puml`: PlantUML file for visualizing the game's class structure.
- `creatures.csv`: Contains data about available Pokémon.
- `items.csv`: Contains data about usable items.
- `locations.csv`: Contains data about game locations.
- `save2024.csv`: Stores the player's saved game data.

---

## Contribution
Contributions are welcome! If you have suggestions for new features or improvements, please:
1. Fork the repository.
2. Create a new branch for your feature.
3. Submit a pull request with a detailed description of your changes.

---
