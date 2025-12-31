# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BTD6 Auto Player - an automated bot for Bloons TD 6 that plays Collection Event maps repeatedly. Uses OCR (Tesseract) to read round numbers from the screen and pyautogui for mouse/keyboard automation.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot (requires BTD6 in fullscreen, switch to game within 5 seconds)
python __main__.py

# Test OCR on sample screenshots
python -m app.img_to_str_reader
```

**External dependency**: Tesseract OCR must be installed on the system.

## Architecture

The bot operates on an event-driven round monitoring system:

1. **`__main__.py`** - Entry point. Sets up logging, starts the round monitor thread, then loops: starting collection games, running map instructions, and handling failures.

2. **`RoundMonitor`** (`app/round_monitor.py`) - Runs in a background thread, continuously captures the round counter region via OCR. When a valid round change is detected, notifies all registered listeners. Tracks consecutive OCR failures to detect game-over states.

3. **`GameController`** (`app/game_controller.py`) - Subscribes to round changes. Executes tower placement/upgrade instructions at milestone rounds defined in map configs. Handles menu navigation (starting maps, collecting rewards, hero selection).

4. **`ImageToTextReader`** (`app/img_to_str_reader.py`) - OCR utility using pytesseract. Preprocesses screenshots (contrast enhancement, inversion, thresholding) before text extraction.

5. **`Settings`** (`app/config/settings.py`) - Loads JSON configuration files.

## Configuration Files

- **`app/config/settings.json`** - Global settings: keyboard shortcuts for towers/upgrades, screen coordinates for UI buttons (round counter position, menu buttons, etc.)

- **`app/config/maps/<MAP_NAME>/impoppable.json`** - Per-map strategy files containing:
  - `towers`: Tower IDs with types and screen coordinates
  - `instructions.start`: Initial tower placements
  - `instructions.milestones`: Array of rounds that trigger actions
  - `instructions.<round>`: Actions to execute at that round

## Instruction Format

Instructions in map configs use a simple DSL:
- `place <tower_id>` - Place a tower
- `upgrade <tower_id> <path> [path...]` - Upgrade tower (1=top, 2=middle, 3=bottom)
- `change <tower_id> <times>` - Change targeting N times

## Screen Coordinate System

All coordinates in config files are absolute screen positions. When adding new maps or adjusting for different screen resolutions, tower coords and button positions need manual calibration.
