"""
Window-specific screenshot capture for macOS using Quartz APIs.
Allows capturing a window even when it's not in the foreground.
"""
import subprocess
import time
import numpy as np
from PIL import Image

try:
    import Quartz
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionAll,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )
    import Quartz.CoreGraphics as CG
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False


class WindowCapture:
    """Capture screenshots from a specific window without requiring focus."""

    def __init__(self, app_name="BloonsTD6"):
        """
        Initialize WindowCapture for a specific application.

        Args:
            app_name: Name of the application to capture (partial match supported)
        """
        self.app_name = app_name
        self._window_id = None
        self._window_bounds = None

        if not QUARTZ_AVAILABLE:
            raise ImportError(
                "Quartz framework not available. Install with: "
                "pip install pyobjc-framework-Quartz"
            )

    def find_window(self):
        """
        Find the window ID and bounds for the target application.

        Returns:
            tuple: (window_id, bounds_dict) or (None, None) if not found
        """
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )

        for window in window_list:
            owner = window.get('kCGWindowOwnerName', '')
            name = window.get('kCGWindowName', '')

            # Match by owner name or window name (case-insensitive partial match)
            if (self.app_name.lower() in owner.lower() or
                self.app_name.lower() in name.lower()):
                window_id = window.get('kCGWindowNumber')
                bounds = window.get('kCGWindowBounds')

                if window_id and bounds:
                    self._window_id = window_id
                    self._window_bounds = bounds
                    return window_id, bounds

        return None, None

    def get_window_id(self):
        """Get cached window ID, refreshing if necessary."""
        if self._window_id is None:
            self.find_window()
        return self._window_id

    def get_window_bounds(self):
        """Get cached window bounds, refreshing if necessary."""
        if self._window_bounds is None:
            self.find_window()
        return self._window_bounds

    def capture_window(self):
        """
        Capture the entire window as a PIL Image.

        Returns:
            PIL.Image: Screenshot of the window, or None if capture failed
                       Image is scaled to match logical points (for Retina compatibility)
        """
        window_id = self.get_window_id()
        if window_id is None:
            # Try to find the window again
            self.find_window()
            window_id = self._window_id
            if window_id is None:
                return None

        # Capture the window
        image_ref = CG.CGWindowListCreateImage(
            CG.CGRectNull,  # Capture entire window
            CG.kCGWindowListOptionIncludingWindow,
            window_id,
            CG.kCGWindowImageBoundsIgnoreFraming
        )

        if image_ref is None:
            # Window might have closed, clear cache and retry once
            self._window_id = None
            self._window_bounds = None
            self.find_window()
            if self._window_id:
                image_ref = CG.CGWindowListCreateImage(
                    CG.CGRectNull,
                    CG.kCGWindowListOptionIncludingWindow,
                    self._window_id,
                    CG.kCGWindowImageBoundsIgnoreFraming
                )
            if image_ref is None:
                return None

        # Convert CGImage to PIL Image
        width = CG.CGImageGetWidth(image_ref)
        height = CG.CGImageGetHeight(image_ref)
        bytes_per_row = CG.CGImageGetBytesPerRow(image_ref)

        pixel_data = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(image_ref))

        # Create numpy array from raw pixel data
        img_array = np.frombuffer(pixel_data, dtype=np.uint8)

        # Reshape: bytes_per_row may include padding
        img_array = img_array.reshape((height, bytes_per_row // 4, 4))
        img_array = img_array[:, :width, :]  # Remove padding

        # Convert BGRA to RGB
        rgb_array = img_array[:, :, [2, 1, 0]]

        image = Image.fromarray(rgb_array)

        # Handle Retina scaling: scale down to match logical points
        # Quartz returns physical pixels, but coordinates are in logical points
        bounds = self.get_window_bounds()
        if bounds:
            logical_width = int(bounds['Width'])
            logical_height = int(bounds['Height'])

            # Check if we need to scale (Retina displays return 2x pixels)
            if width > logical_width or height > logical_height:
                image = image.resize((logical_width, logical_height), Image.Resampling.LANCZOS)

        return image

    def capture_region(self, x, y, width, height):
        """
        Capture a specific region within the window.

        Args:
            x: X offset from window's top-left
            y: Y offset from window's top-left
            width: Width of region to capture
            height: Height of region to capture

        Returns:
            PIL.Image: Screenshot of the region, or None if capture failed
        """
        full_image = self.capture_window()
        if full_image is None:
            return None

        # Crop to the specified region
        return full_image.crop((x, y, x + width, y + height))

    def refresh_window(self):
        """Force refresh of window ID and bounds."""
        self._window_id = None
        self._window_bounds = None
        return self.find_window()

    def get_scale_factors(self, ref_width, ref_height):
        """
        Calculate scale factors from reference resolution to current window size.

        Args:
            ref_width: Reference resolution width
            ref_height: Reference resolution height

        Returns:
            Tuple of (scale_x, scale_y) or (1.0, 1.0) if window not found
        """
        bounds = self.get_window_bounds()
        if not bounds:
            return 1.0, 1.0

        scale_x = bounds['Width'] / ref_width
        scale_y = bounds['Height'] / ref_height
        return scale_x, scale_y

    def scale_to_window(self, x, y, ref_width, ref_height):
        """
        Scale reference coordinates to current window coordinates (window-relative).

        Use this for screenshot region coordinates.

        Args:
            x, y: Coordinates in reference resolution
            ref_width, ref_height: Reference resolution dimensions

        Returns:
            Tuple of (scaled_x, scaled_y) relative to window
        """
        scale_x, scale_y = self.get_scale_factors(ref_width, ref_height)
        return int(x * scale_x), int(y * scale_y)

    def scale_region_to_window(self, x, y, width, height, ref_width, ref_height):
        """
        Scale a region (position + dimensions) to current window size.

        Args:
            x, y: Top-left coordinates in reference resolution
            width, height: Dimensions in reference resolution
            ref_width, ref_height: Reference resolution dimensions

        Returns:
            Tuple of (scaled_x, scaled_y, scaled_width, scaled_height)
        """
        scale_x, scale_y = self.get_scale_factors(ref_width, ref_height)
        return (
            int(x * scale_x),
            int(y * scale_y),
            int(width * scale_x),
            int(height * scale_y)
        )

    def scale_to_screen(self, x, y, ref_width, ref_height):
        """
        Scale reference coordinates to absolute screen coordinates.

        Use this for pyautogui click coordinates.

        Args:
            x, y: Coordinates in reference resolution (relative to game window)
            ref_width, ref_height: Reference resolution dimensions

        Returns:
            Tuple of (screen_x, screen_y) in absolute screen coordinates
        """
        bounds = self.get_window_bounds()
        if not bounds:
            return x, y

        scale_x, scale_y = self.get_scale_factors(ref_width, ref_height)
        screen_x = int(bounds['X'] + x * scale_x)
        screen_y = int(bounds['Y'] + y * scale_y)
        return screen_x, screen_y


class WindowFocus:
    """Utilities for managing window focus on macOS."""

    @staticmethod
    def bring_to_front(app_name, delay=0.3):
        """
        Bring an application to the foreground.

        Args:
            app_name: Name of the application to activate
            delay: Seconds to wait after activation for window to fully focus
        """
        script = f'tell application "{app_name}" to activate'
        subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            timeout=5
        )
        time.sleep(delay)  # Wait for window to fully come to front

    @staticmethod
    def get_frontmost_app():
        """Get the name of the currently frontmost application."""
        script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            return frontApp
        '''
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else None


class FocusManager:
    """
    Context manager for temporarily switching focus to perform input,
    then restoring the previous foreground app.
    """

    def __init__(self, target_app, restore_focus=True):
        """
        Args:
            target_app: Application to switch focus to
            restore_focus: Whether to restore previous app after (default True)
        """
        self.target_app = target_app
        self.restore_focus = restore_focus
        self.previous_app = None

    def __enter__(self):
        if self.restore_focus:
            self.previous_app = WindowFocus.get_frontmost_app()
        WindowFocus.bring_to_front(self.target_app)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.restore_focus and self.previous_app:
            # Brief pause before switching back
            time.sleep(0.05)
            WindowFocus.bring_to_front(self.previous_app)
        return False


def list_windows(app_filter=None):
    """
    Debug utility to list all windows.

    Args:
        app_filter: Optional string to filter by app name
    """
    if not QUARTZ_AVAILABLE:
        print("Quartz not available")
        return

    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)

    print(f"{'Owner':<30} {'Window Name':<40} {'ID':<10}")
    print("-" * 80)

    for window in window_list:
        owner = window.get('kCGWindowOwnerName', '')
        name = window.get('kCGWindowName', '')
        wid = window.get('kCGWindowNumber', '')

        if app_filter and app_filter.lower() not in owner.lower():
            continue

        print(f"{owner:<30} {name:<40} {wid:<10}")


if __name__ == '__main__':
    # Test: list all windows
    print("All visible windows:")
    list_windows()

    print("\n" + "=" * 80 + "\n")

    # Test: try to find and capture BTD6
    print("Attempting to find BloonsTD6 window...")
    try:
        wc = WindowCapture("BloonsTD6")
        wid, bounds = wc.find_window()

        if wid:
            print(f"Found window ID: {wid}")
            print(f"Bounds: {bounds}")

            img = wc.capture_window()
            if img:
                print(f"Captured image size: {img.size}")
                img.save("test_window_capture.png")
                print("Saved to test_window_capture.png")
        else:
            print("BloonsTD6 window not found. Is the game running?")
    except ImportError as e:
        print(f"Error: {e}")
