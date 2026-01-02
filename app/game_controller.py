import time
from . import input_controller
from .config import Settings
from app.img_to_str_reader import ImageToTextReader
from app.window_capture import WindowCapture, WindowFocus, QUARTZ_AVAILABLE

class GameController:
    """
    Handles game logic and responses to round changes.
    This class defines what should happen at different round milestones.
    """
    def __init__(self, round_monitor, logger, background_mode=True):
        self.round_monitor = round_monitor
        # Register our round change handler
        self.round_monitor.add_round_change_listener(self.handle_round_change)
        self.logger = logger
        self.global_settings = Settings().load_global_settings()
        self.map = 'DARKDUNGEONS' # Default map for testing
        self.map_settings = Settings().load_map_settings(self.map, 'impoppable')
        self.milestone_rounds = self.map_settings['instructions']['milestones']
        self.map_ended = False
        self.current_points = 37
        self.points_per_run = 14
        self.points_to_collect = 70

        # Background mode: capture screenshots without focus, only grab focus for input
        self.background_mode = background_mode and QUARTZ_AVAILABLE
        self.app_name = self.global_settings.get('app_name', 'BloonsTD6')

        # Delay after bringing window to focus (seconds)
        self.focus_delay = self.global_settings.get('focus_delay', 0.3)

        # Window capture for background mode
        if QUARTZ_AVAILABLE:
            self.window_capture = WindowCapture(self.app_name)
        else:
            self.window_capture = None

        if self.background_mode:
            self.img_reader = ImageToTextReader(self.window_capture)
            self.logger.info(f"Background mode enabled for '{self.app_name}'")
        else:
            self.img_reader = ImageToTextReader()
            if background_mode and not QUARTZ_AVAILABLE:
                self.logger.warning("Background mode requested but Quartz not available. "
                                    "Install with: pip install pyobjc-framework-Quartz")

    def _ensure_focus(self):
        """Bring the game window to the foreground for input."""
        if self.background_mode:
            WindowFocus.bring_to_front(self.app_name, self.focus_delay)

    def _store_previous_app(self):
        """Store the currently focused app to restore later."""
        if self.background_mode:
            self._previous_app = WindowFocus.get_frontmost_app()

    def _restore_focus(self):
        """Restore focus to the previously active app."""
        if self.background_mode and hasattr(self, '_previous_app') and self._previous_app:
            time.sleep(0.05)
            WindowFocus.bring_to_front(self._previous_app)
            self._previous_app = None

    def _click(self, x, y):
        """Click at the specified coordinates."""
        input_controller.click(x, y)

    def _move_mouse(self, x, y):
        """Move mouse to the specified coordinates."""
        input_controller.moveTo(x, y)

    def _get_region(self, x, y, width, height):
        """Return region coordinates as-is."""
        return (x, y, width, height)

    def handle_round_change(self, current_round):
        """
        Responds to round changes by checking for and executing milestone actions.
        """
        self.logger.info(f"Current round: {current_round}") # For debugging

        remove_rounds = []
        for round in self.milestone_rounds:
            if current_round >= round: # Handle cases where we missed a round due to OCR errors
                self.logger.info(f"Running instructions for round {round}")
                self._store_previous_app()
                self._ensure_focus()
                self.run_instruction_group(self.map_settings['instructions'][str(round)])
                self._restore_focus()
                remove_rounds.append(round)

        for round in remove_rounds:
            self.milestone_rounds.remove(round)

        if current_round >= 99:
            self.logger.info("Second to last or last round! Assuming it takes 30 seconds to finish")
            time.sleep(30)
            self.run_end_map_instructions()
        
    def run_start_map_instructions(self):
        """
        Run the instructions to start the map.
        """
        self.round_monitor.CUR_ROUND = 5 # Reset the round counter for a new map
        self.round_monitor.ROUND_COUNTER_FAILS = 0 # Reset fail counter for new map
        # Reload milestones for the new map cycle (they get removed as they're executed)
        self.map_settings = Settings().load_map_settings(self.map, 'impoppable')
        self.milestone_rounds = list(self.map_settings['instructions']['milestones'])
        instructions = self.map_settings['instructions']['start']
        time.sleep(3)

        self._store_previous_app()
        self._ensure_focus()
        self.run_instruction_group(instructions)
        input_controller.press('space')
        time.sleep(.5)
        input_controller.press('space')
        self._restore_focus()
    
    def run_end_map_instructions(self):
        """
        Run the instructions to end the map and go back to the home screen
        """
        self._store_previous_app()
        self._ensure_focus()

        self.current_points += self.points_per_run
        self.click_at_position('END_GAME_NEXT_BUTTON')
        time.sleep(1)
        self.click_at_position('END_GAME_NEXT_BUTTON')
        time.sleep(1)
        self.click_at_position('END_GAME_HOME_BUTTON')
        time.sleep(2)
        if self.current_points >= self.points_to_collect:
            self.click_at_position('COLLECT_INSTA')
            time.sleep(1)
            self.click_at_position('3INSTA1')
            time.sleep(1)
            self.click_at_position('3INSTA1')
            time.sleep(1)
            self.click_at_position('3INSTA2')
            time.sleep(1)
            self.click_at_position('3INSTA2')
            time.sleep(1)
            self.click_at_position('3INSTA3')
            time.sleep(1)
            self.click_at_position('3INSTA3')
            time.sleep(1)
            self.click_at_position('2INSTA1')
            time.sleep(1)
            self.click_at_position('2INSTA1')
            time.sleep(1)
            self.click_at_position('2INSTA2')
            time.sleep(1)
            self.click_at_position('2INSTA2')
            time.sleep(1)
            self.click_at_position('INSTASELECTOK')
            time.sleep(1)
            self.click_at_position('BACK_BUTTON')
            time.sleep(2)
            self.current_points -= self.points_to_collect
        self.map_ended = True

        self._restore_focus()

    def run_instruction_group(self, instructions):
        """Run group of instructions.

        Args:
            instructions (list): List of instructions to run.
        """
        self.logger.info(f"Running instructions: {instructions}")
        for full_instruction in instructions:
            instruction = full_instruction.split(' ')
            instruction_type = instruction[0]

            if instruction_type == 'place':
                self.place_tower(instruction[1])
            elif instruction_type == 'upgrade':
                self.upgrade_tower(instruction[1], instruction[2:])
            elif instruction_type == 'change':
                self.change_tower_targeting(instruction[1], instruction[2])

            time.sleep(.5) # Wait for the game to catch up
    
    def place_tower(self, tower_id):
        """Place a tower on the map.

        Args:
            tower_name (str): ID of the tower to place.
        """
        self.logger.info(f"Placing {tower_id}")

        pos = self.map_settings['towers'][tower_id]['coords']
        tower_type = self.map_settings['towers'][tower_id]['type']
        shortcut = self.global_settings['tower_shortcuts'][tower_type]

        # Move mouse to target position first to ensure game receives keyboard input
        self._move_mouse(pos[0], pos[1])

        input_controller.press(shortcut)
        if tower_type == 'HERO':
            time.sleep(1)  # Hero menu takes longer to load
            input_controller.press(shortcut)
            time.sleep(1)
            input_controller.press(shortcut)
        time.sleep(1.0)
        input_controller.press(shortcut)
        time.sleep(1.0)
        self._click(pos[0], pos[1])

    def upgrade_tower(self, tower_id, upgrade_paths):
        """Upgrade a tower on the map.

        Args:
            tower_id (str): ID of the tower to upgrade.
            upgrade_id (list): List of the upgrades to apply.
                              1 is top path, 2 is middle, 3 is bottom.
        """
        self.logger.info(f"Upgrading {tower_id} on path {upgrade_paths}")
        pos = self.map_settings['towers'][tower_id]['coords']
        self._click(pos[0], pos[1])
        time.sleep(1.0)  # Wait for tower selection UI to appear (longer for VM)

        for upgrade_path in upgrade_paths:
            upgrade_path = int(upgrade_path)
            upgrade_path = 'UPGRADE_TOP' if upgrade_path == 1 else 'UPGRADE_MIDDLE' if upgrade_path == 2 else 'UPGRADE_BOTTOM'

            upgrade_shortcut = self.global_settings['tower_shortcuts'][upgrade_path]
            time.sleep(0.5)
            input_controller.press(upgrade_shortcut)
            time.sleep(0.5)
        time.sleep(0.3)
        input_controller.press('esc')

    def change_tower_targeting(self, tower_id, target_change_times):
        """Change the targeting of a tower on the map.

        Args:
            tower_id (str): ID of the tower to upgrade.
            target_change_times (str): Str rep of the number of times to change targeting for a tower.
        """
        self.logger.info(f"Changing {tower_id} targeting {target_change_times} times")
        pos = self.map_settings['towers'][tower_id]['coords']
        self._click(pos[0], pos[1])
        time.sleep(0.5)  # Wait for tower selection UI to appear

        for i in range(int(target_change_times)):
            input_controller.press('tab')
            time.sleep(.1)
        input_controller.press('esc')

    def start_dark_dungeons_game(self):
        """
        Starts the dark dungeons game.
        """
        self._store_previous_app()
        self._ensure_focus()
        self.click_at_position('HOME_PLAY_BUTTON')
        time.sleep(.3)
        self.click_at_position('MAP_GO_LEFT_BUTTON')
        time.sleep(.3)
        self.click_at_position('MAP_GO_LEFT_BUTTON')
        time.sleep(.3)
        self.click_at_position('MAP_GO_LEFT_BUTTON')
        time.sleep(.3)
        self.click_at_position('MAP_SELECT_TOPRIGHT')
        time.sleep(.3)
        self.click_at_position('HARD_MODE_SELECT')
        time.sleep(.3)
        self.click_at_position('IMPOPPABLE_MODE_SELECT')
        time.sleep(.3)
        self.click_at_position('MAP_OVERWRITE_SAVE')
        time.sleep(4)
        self.click_at_position('IMPOPPABLE_GAMESTART_OK')
        self._restore_focus()

    def start_collection_game(self):
        """
        Checks the collection game mode to determine current map
        Also selects hero and enters into the map.
        """
        self._store_previous_app()
        self._ensure_focus()

        self.click_at_position('COLLECTION_EVENT_SELECT')
        self.click_at_position('COLLECTION_EVENT_START')
        time.sleep(1)

        # Determine map selection, and update class map variables
        # Note: In background mode, screenshot capture works without focus
        map_region = self._get_region(
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPERT_MAP_TOPLEFT'][0],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPERT_MAP_TOPLEFT'][1],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPER_MAP_DIMENSIONS'][0],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPER_MAP_DIMENSIONS'][1]
        )
        ocr_map_name = self.img_reader.extract_text_from_region(
            map_region[0], map_region[1], map_region[2], map_region[3],
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        )
        self.logger.info(f"OCR map name: {ocr_map_name}")

        # Use fuzzy matching to find the best map match
        cutoff = self.global_settings.get('map_match_cutoff', 0.75)
        matched_map, score = Settings().find_best_map_match(ocr_map_name, cutoff)

        if matched_map:
            if matched_map != ocr_map_name:
                self.logger.info(f"Fuzzy matched '{ocr_map_name}' -> '{matched_map}' (score: {score:.2f})")
            self.map = matched_map
        else:
            self.logger.warning(f"No map match found for '{ocr_map_name}' with cutoff {cutoff}. Using raw OCR text.")
            self.map = ocr_map_name

        self.map_settings = Settings().load_map_settings(self.map, 'impoppable')
        self.milestone_rounds = self.map_settings['instructions']['milestones']

        # Select relevant hero for map
        self.click_at_position('HERO_SELECT_IN_MAP_SELECT')
        self.click_at_position(f'{self.map_settings["hero"]}_SELECT')
        self.click_at_position('HERO_SELECT_CONFIRM')
        self.click_at_position('BACK_BUTTON')
        self.click_at_position('BACK_BUTTON')

        # Start map in impoppable mode
        self.click_at_position('COLLECTION_EVENT_START')
        self.click_at_position('COLLECTION_EVENT_EXPERT_MAP_SELECT')
        self.click_at_position('HARD_MODE_SELECT')
        self.click_at_position('IMPOPPABLE_MODE_SELECT')
        self.click_at_position('MAP_OVERWRITE_SAVE') # In case there's a save file to overwrite
        time.sleep(4) # Wait for map to load
        self.click_at_position('IMPOPPABLE_GAMESTART_OK')

        self._restore_focus()

    def click_at_position(self, selection):
        pos = self.global_settings['button_positions'][selection]
        self.logger.info(f"Clicking {selection} at ({pos[0]}, {pos[1]})")
        input_controller.click(pos[0], pos[1])
        time.sleep(.5)