import pyautogui
import time
import random
from datetime import datetime
from zoneinfo import ZoneInfo

# ANSI Color Codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Disable fail-safe as requested
pyautogui.FAILSAFE = False

def move_mouse_periodically(interval_seconds):
    """
    Moves the mouse cursor to a random location every interval_seconds.
    """
    # Get current screen size
    screen_width, screen_height = pyautogui.size()
    
    print(f"\n{BOLD}{CYAN}--- MOUSEMOVE STARTING ---{RESET}")
    print(f"{BOLD}Screen Size:{RESET} {screen_width}x{screen_height}")
    print(f"{BOLD}Interval:{RESET} {interval_seconds} seconds")
    print(f"{BOLD}Timezone:{RESET} CST (US/Central)")
    print(f"{YELLOW}To stop: Press Ctrl+C{RESET}\n")
    
    # Range for randomization: 0 to screen_size - 10px
    max_x = max(0, screen_width - 10)
    max_y = max(0, screen_height - 10)
    
    try:
        while True:
            # Get current position
            start_pos = pyautogui.position()
            
            # Generate random coordinates
            target_x = random.randint(0, max_x)
            target_y = random.randint(0, max_y)
            
            # Move mouse cursor to the random location
            pyautogui.moveTo(target_x, target_y, duration=0.2)
            
            # Get new position
            end_pos = pyautogui.position()
            
            # Print timestamped movement information (CST time zone)
            timestamp = datetime.now(ZoneInfo("US/Central")).strftime("%I:%M:%S %p")
            print(f"[{BLUE}{timestamp}{RESET}] "
                  f"{GREEN}Move:{RESET} "
                  f"(X: {start_pos.x:4}, Y: {start_pos.y:4}) "
                  f"{MAGENTA}→{RESET} "
                  f"(X: {end_pos.x:4}, Y: {end_pos.y:4})")
            
            # Wait for the next interval
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Script stopped by user.{RESET}")

if __name__ == "__main__":
    # Five minutes = 300 seconds
    INTERVAL = 300
    move_mouse_periodically(INTERVAL)
