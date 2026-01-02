import time, logging, sys
from app.game_controller import GameController
from app.round_monitor import RoundMonitor
from app.config import Settings
from app.img_to_str_reader import ImageToTextReader
from app.window_capture import WindowCapture, QUARTZ_AVAILABLE

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

    # Setup background mode if available (captures screenshots without focus)
    settings = Settings().load_global_settings()
    background_mode = settings.get('background_mode', True) and QUARTZ_AVAILABLE
    app_name = settings.get('app_name', 'BloonsTD6')

    if background_mode:
        logger.info(f"Background mode enabled - capturing '{app_name}' window")
        window_capture = WindowCapture(app_name)
        img_reader = ImageToTextReader(window_capture)
    else:
        logger.info("Background mode disabled - using screen capture (game must be in foreground)")
        window_capture = None
        img_reader = ImageToTextReader()

    round_monitor = RoundMonitor(logger, img_reader, window_capture)
    game_controller = GameController(round_monitor, logger, background_mode)
    # Share the img_reader and window_capture with game_controller
    game_controller.img_reader = img_reader
    game_controller.window_capture = window_capture

    if not background_mode:
        time.sleep(5) # Give 5 seconds to switch to the game window
    #game_controller.run_start_map_instructions()
    #round_monitor.start_monitoring()
    
    round_monitor.start_monitoring()
    while True:
        logger.info("$$$$ Starting new map")
        game_controller.map_ended = False
        #game_controller.start_collection_game()
        game_controller.start_dark_dungeons_game()
        game_controller.run_start_map_instructions()

        # 3 minutes of failed OCR likely means defeat
        while round_monitor.ROUND_COUNTER_FAILS <= 360 and not game_controller.map_ended:
            # At 2 minutes of failures (240), try to clear level up screen (once)
            if round_monitor.ROUND_COUNTER_FAILS == 240:
                logger.info(f"Failed 2 minutes of OCR, assuming level up screen")
                game_controller.click_at_position('INSTASELECTOK')
            time.sleep(.5)

        # If loop exited due to OCR failures (not map_ended), assume defeat
        if round_monitor.ROUND_COUNTER_FAILS > 360 and not game_controller.map_ended:
            logger.info(f"Failed 3 minutes of OCR, assuming defeat - going back home")
            game_controller.click_at_position('DEFEAT_GAME_HOME_BUTTON')
            game_controller.map_ended = True
            time.sleep(3)   