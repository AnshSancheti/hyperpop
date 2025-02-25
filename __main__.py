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
    logger.info('-----------Starting BTD6 Auto Player------------')

    round_monitor = RoundMonitor(logger)
    game_controller = GameController(round_monitor, logger)

    time.sleep(5) # Give 5 seconds to switch to the game window
    #game_controller.run_start_map_instructions()
    #round_monitor.start_monitoring()
    
    round_monitor.start_monitoring()
    while True:
        logger.info("$$$$ Starting new map")
        game_controller.map_ended = False
        game_controller.start_collection_game()
        game_controller.run_start_map_instructions()

        # 2 minutes of failed round counter likely means game is over, go home
        while round_monitor.ROUND_COUNTER_FAILS <= 300 and not game_controller.map_ended:
            if round_monitor.ROUND_COUNTER_FAILS > 0 and round_monitor.ROUND_COUNTER_FAILS % 180 == 0:
                logger.info(f"Failed 1.5 minutes of OCR, assuming level up screen")
                # arbitrary clicks to get through level up screen
                game_controller.click_at_position('INSTASELECTOK') 
                game_controller.click_at_position('INSTASELECTOK')
            time.sleep(.5) 

        if round_monitor.ROUND_COUNTER_FAILS > 600:
            logger.info(f"Failed 5 minutes of OCR, assuming game over and goign back home")
            game_controller.click_at_position('DEFEAT_GAME_HOME_BUTTON')
            round_monitor.ROUND_COUNTER_FAILS = 0
            time.sleep(3)   