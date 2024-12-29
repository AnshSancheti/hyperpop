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
        
        # Define milestone actions in a dictionary
        self.milestone_actions = {
            5: self.milestone_five_action,
            10: self.milestone_ten_action,
            15: self.milestone_fifteen_action
        }

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

        self.click_at_position(self.global_settings, 'COLLECTION_EVENT_EXPERT_MAP_SELECT')
        self.click_at_position(self.global_settings, 'HARD_MODE_SELECT')

        
        #self.click_at_position(self.global_settings, 'IMPOPPABLE_MODE_SELECT')
        #time.sleep(4) # Wait for map to load
        #self.click_at_position(self.global_settings, 'IMPOPPABLE_GAMESTART_OK')

    def handle_round_change(self, current_round):
        """
        Responds to round changes by checking for and executing milestone actions.
        """
        self.logger.info(f"Current round: {current_round}")  # For debugging
        
        if current_round in self.milestone_actions:
            self.milestone_actions[current_round]()

    # Define specific milestone actions
    def milestone_five_action(self):
        self.logger.info("Round 5 action: Spawning extra enemies!")
        # Add specific game logic here

    def milestone_ten_action(self):
        print("Round 10 action: Activating power-ups!")
        # Add specific game logic here

    def milestone_fifteen_action(self):
        print("Round 15 action: Boss battle starting!")
        # Add specific game logic here

    def click_at_position(self, settings, selection):
        pos = settings['button_positions'][selection]
        self.logger.info(f"Clicking {selection}")
        pyautogui.click(pos[0], pos[1])
        time.sleep(1)