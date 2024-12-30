import time, pyautogui
from .config import Settings
from app.img_to_str_reader import ImageToTextReader

class GameController:
    """
    Handles game logic and responses to round changes.
    This class defines what should happen at different round milestones.
    """
    def __init__(self, round_monitor, logger):
        self.round_monitor = round_monitor
        # Register our round change handler
        self.round_monitor.add_round_change_listener(self.handle_round_change)
        self.logger = logger
        self.global_settings = Settings().load_global_settings()
        self.map = 'DARKCASTLE' # Default map for testing
        self.map_settings = Settings().load_map_settings(self.map, 'impoppable')
        self.milestone_rounds = self.map_settings['instructions']['milestones']

    def handle_round_change(self, current_round):
        """
        Responds to round changes by checking for and executing milestone actions.
        """
        self.logger.info(f"Current round: {current_round}") # For debugging
        
        remove_rounds = []
        for round in self.milestone_rounds:
            if current_round >= round: # Handle cases where we missed a round due to OCR errors
                self.logger.info(f"Running instructions for round {round}")
                self.run_instruction_group(self.map_settings['instructions'][str(round)])
                remove_rounds.append(round)
        
        for round in remove_rounds:
            self.milestone_rounds.remove(round)
        
        print(f"Remaining milestone rounds: {self.milestone_rounds}")

    def run_start_map_instructions(self):
        """
        Run the instructions to start the map.
        """
        instructions = self.map_settings['instructions']['start']
        self.run_instruction_group(instructions)
        pyautogui.press('space') 
        time.sleep(.5)
        pyautogui.press('space')

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
                self.upgrade_tower(instruction[1], int(instruction[2]))

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

        pyautogui.press(shortcut)
        time.sleep(.2)
        pyautogui.click(pos[0], pos[1])

    def upgrade_tower(self, tower_id, upgrade_path):
        """Upgrade a tower on the map.

        Args:
            tower_id (str): ID of the tower to upgrade.
            upgrade_id (str): Path of the upgrade to apply. 
                              1 is top path, 2 is middle, 3 is bottom.
        """
        self.logger.info(f"Upgrading {tower_id} on path {upgrade_path}")

        pos = self.map_settings['towers'][tower_id]['coords']
        upgrade_path = 'UPGRADE_TOP' if upgrade_path == 1 else 'UPGRADE_MIDDLE' if upgrade_path == 2 else 'UPGRADE_BOTTOM'

        upgrade_shortcut = self.global_settings['tower_shortcuts'][upgrade_path]
        pyautogui.click(pos[0], pos[1])
        time.sleep(.2)
        pyautogui.press(upgrade_shortcut)
        time.sleep(.2)
        pyautogui.press('esc')

    def start_collection_game(self):
        """
        Start the game by clicking on the hero selection button.
        """
        self.click_at_position(self.global_settings, 'COLLECTION_EVENT_SELECT')
        self.click_at_position(self.global_settings, 'COLLECTION_EVENT_START')
        # Determine map selection
        map_name = ImageToTextReader().extract_text_from_region(
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPERT_MAP_TOPLEFT'][0],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPERT_MAP_TOPLEFT'][1],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPER_MAP_DIMENSIONS'][0],
            self.global_settings['button_positions']['COLLECTION_EVENT_EXPER_MAP_DIMENSIONS'][1],
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        )
        self.logger.info(f"Map name: {map_name}")
        self.map = map_name
        self.map_settings = Settings().load_map_settings(self.map, 'impoppable')
        self.milestone_rounds = self.map_settings['instructions']['milestones']

        self.click_at_position(self.global_settings, 'COLLECTION_EVENT_EXPERT_MAP_SELECT')
        self.click_at_position(self.global_settings, 'HARD_MODE_SELECT')

        #self.click_at_position(self.global_settings, 'IMPOPPABLE_MODE_SELECT')
        #time.sleep(4) # Wait for map to load
        #self.click_at_position(self.global_settings, 'IMPOPPABLE_GAMESTART_OK')

    def click_at_position(self, settings, selection):
        pos = settings['button_positions'][selection]
        self.logger.info(f"Clicking {selection}")
        pyautogui.click(pos[0], pos[1])
        time.sleep(1)