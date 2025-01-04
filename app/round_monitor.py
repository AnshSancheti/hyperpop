import threading
import time
from .config import Settings
from app.img_to_str_reader import ImageToTextReader

class RoundMonitor:
    """
    A dedicated class for monitoring and tracking the current round.
    This class has a single responsibility: maintaining the round counter.
    It notifies listeners when the round changes but doesn't know about specific actions.
    """
    def __init__(self, logger):
        self.CUR_ROUND = 5 # Impoppable mode starts at round 6
        self.ROUND_COUNTER_FAILS = 0
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
            settings = Settings().load_global_settings()
            round_counter = ImageToTextReader().extract_text_from_region(
                settings['button_positions']['ROUND_COUNTER'][0],
                settings['button_positions']['ROUND_COUNTER'][1],
                settings['button_positions']['ROUND_DIMENSIONS'][0],
                settings['button_positions']['ROUND_DIMENSIONS'][1]
            )

            if round_counter is not None:
                round_counter = round_counter.split('/')

            # Run validation for round counter since OCR can be unreliable
            if (round_counter is not None 
                and len(round_counter) > 1 # ensure we have a fraction
                and round_counter[0].isdigit() # ensure the cur round is a number
                and int(round_counter[0]) <= 100 # ensure the cur round is within bounds
                and round_counter[1].isdigit() # ensure the total rounds is a number
                and int(round_counter[1]) == 100 # ensure the total rounds is 100
                and int(round_counter[0]) > self.CUR_ROUND # ensure the round has changed...
                and int(round_counter[0]) < self.CUR_ROUND + 30 # ...but not by too much
                and int(round_counter[0]) != self.CUR_ROUND + 10
                and int(round_counter[0]) != self.CUR_ROUND + 11): # special cases for Ravine, 7->17
                self.CUR_ROUND = int(round_counter[0])
                self._notify_round_change()
                self.ROUND_COUNTER_FAILS = 0
            else:
                self.ROUND_COUNTER_FAILS += 1

            time.sleep(.5)

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