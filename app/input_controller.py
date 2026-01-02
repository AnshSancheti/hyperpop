"""
Input controller using pynput for mouse and keyboard operations.
This replaces pyautogui for input in VM environments where pyautogui doesn't work.
"""
import time
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# Global controllers
_mouse = MouseController()
_keyboard = KeyboardController()

# Mapping of string key names to pynput Key objects
_SPECIAL_KEYS = {
    'space': Key.space,
    'enter': Key.enter,
    'return': Key.enter,
    'tab': Key.tab,
    'esc': Key.esc,
    'escape': Key.esc,
    'backspace': Key.backspace,
    'delete': Key.delete,
    'up': Key.up,
    'down': Key.down,
    'left': Key.left,
    'right': Key.right,
    'shift': Key.shift,
    'ctrl': Key.ctrl,
    'alt': Key.alt,
    'cmd': Key.cmd,
    'command': Key.cmd,
}


def click(x, y, clicks=1, button='left'):
    """
    Click at the specified coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        clicks: Number of clicks (default 1)
        button: 'left' or 'right' (default 'left')
    """
    _mouse.position = (x, y)
    time.sleep(0.05)  # Small delay to ensure position is set

    btn = Button.left if button == 'left' else Button.right
    for _ in range(clicks):
        _mouse.click(btn)
        time.sleep(0.05)


def moveTo(x, y):
    """
    Move the mouse to the specified coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
    """
    _mouse.position = (x, y)


def press(key):
    """
    Press and release a key.

    Args:
        key: Key to press (string). Can be a single character or special key name
             like 'space', 'esc', 'tab', 'enter', etc.
    """
    # Check if it's a special key
    if key.lower() in _SPECIAL_KEYS:
        pynput_key = _SPECIAL_KEYS[key.lower()]
    else:
        # Single character key
        pynput_key = key

    _keyboard.press(pynput_key)
    time.sleep(0.1)  # Longer hold for VM to register
    _keyboard.release(pynput_key)


def typewrite(text, interval=0.05):
    """
    Type a string of characters.

    Args:
        text: String to type
        interval: Delay between keystrokes (default 0.05)
    """
    for char in text:
        _keyboard.press(char)
        _keyboard.release(char)
        time.sleep(interval)


def mouseDown(x=None, y=None, button='left'):
    """
    Press and hold the mouse button.

    Args:
        x: Optional X coordinate to move to first
        y: Optional Y coordinate to move to first
        button: 'left' or 'right' (default 'left')
    """
    if x is not None and y is not None:
        _mouse.position = (x, y)
        time.sleep(0.05)

    btn = Button.left if button == 'left' else Button.right
    _mouse.press(btn)


def mouseUp(x=None, y=None, button='left'):
    """
    Release the mouse button.

    Args:
        x: Optional X coordinate to move to first
        y: Optional Y coordinate to move to first
        button: 'left' or 'right' (default 'left')
    """
    if x is not None and y is not None:
        _mouse.position = (x, y)
        time.sleep(0.05)

    btn = Button.left if button == 'left' else Button.right
    _mouse.release(btn)


def position():
    """
    Get the current mouse position.

    Returns:
        tuple: (x, y) coordinates
    """
    return _mouse.position


def size():
    """
    Get the screen size.

    Note: This uses Quartz on macOS. Falls back to a default if unavailable.

    Returns:
        tuple: (width, height)
    """
    try:
        import Quartz
        main_display = Quartz.CGMainDisplayID()
        width = Quartz.CGDisplayPixelsWide(main_display)
        height = Quartz.CGDisplayPixelsHigh(main_display)
        return (width, height)
    except ImportError:
        # Fallback: try pyautogui just for size (doesn't require input permissions)
        try:
            import pyautogui
            return pyautogui.size()
        except:
            return (1920, 1080)  # Default fallback
