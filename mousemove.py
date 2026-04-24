import pyautogui
import time
import random
from datetime import datetime
from zoneinfo import ZoneInfo

INTERVAL = 300  # seconds between moves (5 minutes)
TIMEZONE = ZoneInfo("US/Central")

# ANSI Color Codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

pyautogui.FAILSAFE = False


def compute_bounds(screen_width: int, screen_height: int) -> tuple[int, int]:
    """Return the max mouse coordinates with a 10px safety margin from screen edges."""
    return max(0, screen_width - 10), max(0, screen_height - 10)


def get_timestamp(timezone: ZoneInfo) -> str:
    """Return the current time formatted as HH:MM:SS AM/PM in the given timezone."""
    return datetime.now(timezone).strftime("%I:%M:%S %p")


def format_move_log(timestamp: str, start_pos, end_pos) -> str:
    """Format a single mouse-move log line with ANSI colours."""
    return (
        f"[{BLUE}{timestamp}{RESET}] "
        f"{GREEN}Move:{RESET} "
        f"(X: {start_pos.x:4}, Y: {start_pos.y:4}) "
        f"{MAGENTA}→{RESET} "
        f"(X: {end_pos.x:4}, Y: {end_pos.y:4})"
    )


def print_startup_banner(
    screen_width: int,
    screen_height: int,
    interval_seconds: int,
    timezone: ZoneInfo,
) -> None:
    """Print the startup banner showing screen dimensions, interval, and timezone."""
    print(f"\n{BOLD}{CYAN}--- MOUSEMOVE STARTING ---{RESET}")
    print(f"{BOLD}Screen Size:{RESET} {screen_width}x{screen_height}")
    print(f"{BOLD}Interval:{RESET} {interval_seconds} seconds")
    print(f"{BOLD}Timezone:{RESET} {timezone.key}")
    print(f"{YELLOW}To stop: Press Ctrl+C{RESET}\n")


def move_mouse_periodically(interval_seconds: int) -> None:
    """Move the mouse to a random screen position every interval_seconds seconds."""
    screen_width, screen_height = pyautogui.size()
    max_x, max_y = compute_bounds(screen_width, screen_height)

    print_startup_banner(screen_width, screen_height, interval_seconds, TIMEZONE)

    try:
        while True:
            start_pos = pyautogui.position()
            pyautogui.moveTo(random.randint(0, max_x), random.randint(0, max_y), duration=0.2)
            end_pos = pyautogui.position()

            timestamp = get_timestamp(TIMEZONE)
            print(format_move_log(timestamp, start_pos, end_pos))

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Script stopped by user.{RESET}")


if __name__ == "__main__":
    move_mouse_periodically(INTERVAL)
