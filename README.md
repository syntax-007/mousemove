# mousemove

A simple Python script to prevent screen locks or idle states by moving the mouse cursor to a random location at a configurable interval (default: 5 minutes).

## Features
- Moves the mouse cursor to a random location at the configured interval.
- Prints the start and end coordinates of each move with a colorful timestamp.
- Interval is configurable via a command-line argument.

## Setup

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Run the script:**
    ```bash
    python mousemove.py           # defaults to 300 seconds (5 minutes)
    python mousemove.py 60        # move every 60 seconds
    ```

3. **Stop the script:** Press `Ctrl+C`.

## Development

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/
```

Format code with black:

```bash
black mousemove.py tests/
```

## Notes
- `pyautogui` may require Accessibility permissions on macOS (System Settings → Privacy & Security → Accessibility).
