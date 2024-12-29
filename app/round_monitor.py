import threading
import time
import pyautogui
import pytesseract
from PIL import Image
import numpy as np
from .config import Settings

class RoundMonitor:
    """
    A dedicated class for monitoring and tracking the current round.
    This class has a single responsibility: maintaining the round counter.
    It notifies listeners when the round changes but doesn't know about specific actions.
    """
    def __init__(self, logger):
        self.CUR_ROUND = 6 # Impoppable mode starts at round 6
        self._running = False
        self._thread = None
        self.logger = logger
        # List to store callback functions that want to be notified of round changes
        self._round_change_callbacks = []

    def add_round_change_listener(self, callback):
        """
        Register a function to be called whenever the round changes.
        The callback function should accept a single parameter: the new round number.
        """
        self._round_change_callbacks.append(callback)

    def _notify_round_change(self):
        """
        Notify all registered listeners about the round change.
        This encapsulates how we handle notifications.
        """
        for callback in self._round_change_callbacks:
            callback(self.CUR_ROUND)

    def round_counter(self):
        """
        Main counter function that runs in its own thread.
        Only responsible for incrementing the round and notifying listeners.
        """
        while self._running:
            round_counter = self.extract_text_from_region(
                Settings.settings['button_positions']['ROUND_COUNTER'][0],
                Settings.settings['button_positions']['ROUND_COUNTER'][1],
                Settings.settings['button_positions']['ROUND_DIMENSIONS'][0],
                Settings.settings['button_positions']['ROUND_DIMENSIONS'][1]
            )

            self.logger.info(f"Round counter: {round_counter}")
            round_counter = str(round).split('/')
            self.logger.info(f"Round counter: {round_counter}")

            if len(round_counter) > 1 and round_counter[0].isdigit():
                self.CUR_ROUND += round_counter[0]
                self._notify_round_change()

            time.sleep(1)

    def start_monitoring(self):
        """Start the round counter in a separate thread."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self.round_counter)
            self._thread.start()

    def stop_monitoring(self):
        """Safely stop the round counter."""
        self._running = False
        if self._thread:
            self._thread.join()

    def extract_text_from_region(self, x, y, width, height) -> str:
        """
        Capture a specific region of the screen and extract text from it using OCR.
        
        Args:
            x (int): The x-coordinate of the top-left corner of the region
            y (int): The y-coordinate of the top-left corner of the region
            width (int): The width of the region to capture
            height (int): The height of the region to capture
        
        Returns:
            str: Extracted text from the captured region
        """
        try:
            # Take a screenshot of the specified region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert the screenshot to a format pytesseract can process
            # We'll convert to RGB to ensure compatibility
            screenshot = screenshot.convert('RGB')
            
            # Extract text from the image
            text = pytesseract.image_to_string(
                screenshot, 
                config=f"-c tessedit_char_whitelist=0123456789/ --psm 7", 
                nice=1)
            
            return text.strip()
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
