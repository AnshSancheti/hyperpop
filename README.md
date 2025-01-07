# BTD6 Auto Player
An automated player for Bloons TD 6 that helps collect rewards from Collection Events. The bot uses computer vision and automation to play maps repeatedly.

## Features
Automatically plays BTD6 Collection Event maps
Configurable strategies per map via JSON files
Round detection using OCR (Optical Character Recognition)
Automated hero placement and tower management
Handles game menus and map selection
Logging system to track progress and debugging

## Setup
1.  Install required dependencies using
```
pip install -r requirements.txt
```
2. Install Tesseract OCR for your operating system (required for reading game text)
3. Configure map strategies in maps directory. Current map strategies may not map to your computer screen and will require adjustment.
4. run with ```python __main__.py```


## Project Structure
```
app/
├── config/               # Configuration files
│   └── maps/             # Map-specific strategy JSONs
├── game_controller.py    # Main controller for tower placement/menu management
├── img_to_str_reader.py  # OCR code to determine current round and map name
└── round_monitor.py      # Round change event monitor
```

## TODO

- [x] Initialize git repo and logging
- [x] Get mouse to click on screen
- [x] Screengrab round counter
- [x] Read from screengrab to determine round #
- [x] Set up event handling for round changes
- [x] Click into a map
- [x] JSON config for per-map strategy
- [x] Validate strategy JSONs
- [x] Get into a collection event map
- [x] Add menu handling for insta monkey collecting
- [ ] Confirm stability when map defeats happen
- [x] Confirm stability when level ups occur
- [ ] Handle OCR map name variations
- [ ] Update JSON to remove "milestones" array