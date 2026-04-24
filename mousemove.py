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


def move_mouse_periodically(interval_seconds):
    screen_width, screen_height = pyautogui.size()
    max_x = max(0, screen_width - 10)
    max_y = max(0, screen_height - 10)

    print(f"\n{BOLD}{CYAN}--- MOUSEMOVE STARTING ---{RESET}")
    print(f"{BOLD}Screen Size:{RESET} {screen_width}x{screen_height}")
    print(f"{BOLD}Interval:{RESET} {interval_seconds} seconds")
    print(f"{BOLD}Timezone:{RESET} {TIMEZONE.key}")
    print(f"{YELLOW}To stop: Press Ctrl+C{RESET}\n")

    try:
        while True:
            start_pos = pyautogui.position()
            pyautogui.moveTo(random.randint(0, max_x), random.randint(0, max_y), duration=0.2)
            end_pos = pyautogui.position()

            timestamp = datetime.now(TIMEZONE).strftime("%I:%M:%S %p")
            print(f"[{BLUE}{timestamp}{RESET}] "
                  f"{GREEN}Move:{RESET} "
                  f"(X: {start_pos.x:4}, Y: {start_pos.y:4}) "
                  f"{MAGENTA}→{RESET} "
                  f"(X: {end_pos.x:4}, Y: {end_pos.y:4})")

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Script stopped by user.{RESET}")


if __name__ == "__main__":
    move_mouse_periodically(INTERVAL)
