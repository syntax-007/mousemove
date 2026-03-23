# mousemove

A simple Python script to prevent screen locks or idle states by moving the mouse cursor to a random location every five minutes.

## Features
- Prints the current screen size on startup.
- Moves the mouse cursor to a random location (between 0 and screen size - 10px) every 5 minutes.
- Prints the start and end coordinates of each move with a colorful timestamp and formatting.

## Setup

1.  **Install dependencies:**
    Ensure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the script:**
    ```bash
    python mousemove.py
    ```

## Notes
- `pyautogui` may require additional system permissions to control the mouse on macOS and Linux (e.g., Accessibility permissions in macOS System Settings).
- **To stop the script:** Press `Ctrl+C` in your terminal.
