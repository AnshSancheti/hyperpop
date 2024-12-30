import time, logging, sys
from app.game_controller import GameController
from app.round_monitor import RoundMonitor
from app.config import Settings

def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log.txt', mode='a')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger

if __name__ == '__main__':
    logger = setup_logger('btd6')
    logger.info('----Starting BTD6 Auto Clicker----')

    round_monitor = RoundMonitor(logger)
    game_controller = GameController(round_monitor, logger)

    time.sleep(5) # Give 5 seconds to switch to the game window
    while True:
        game_controller.start_collection_game()
        # start monitoring once game has started
        round_monitor.start_monitoring()
        game_controller.run_start_map_instructions()
        round_monitor.stop_monitoring()
