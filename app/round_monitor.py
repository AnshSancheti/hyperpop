import threading
import time

class RoundMonitor:
    """
    A dedicated class for monitoring and tracking the current round.
    This class has a single responsibility: maintaining the round counter.
    It notifies listeners when the round changes but doesn't know about specific actions.
    """
    def __init__(self, logger):
        self.CUR_ROUND = 0
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
            self.CUR_ROUND += 1
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
