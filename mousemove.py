import argparse
import pyautogui
import time
import random
from datetime import datetime
from typing import Any, ClassVar

from pyautogui import Size
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class Config(BaseModel):
    interval_seconds: int = 300
    screen_margin: int = 10
    move_duration: float = 0.2


# ---------------------------------------------------------------------------
# Mouse abstraction (DIP: isolates pyautogui from the orchestrator)
# ---------------------------------------------------------------------------


class MouseController(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    config: Config

    def model_post_init(self, __context: Any) -> None:
        pyautogui.FAILSAFE = False

    @staticmethod
    def screen_size() -> Size:
        return pyautogui.size()

    @staticmethod
    def current_position():
        return pyautogui.position()

    def move_to_random(self, max_x: int, max_y: int) -> None:
        pyautogui.moveTo(
            random.randint(0, max_x),
            random.randint(0, max_y),
            duration=self.config.move_duration,
        )

    def compute_bounds(self, screen_width: int, screen_height: int) -> tuple[int, int]:
        return (
            max(0, screen_width - self.config.screen_margin),
            max(0, screen_height - self.config.screen_margin),
        )


# ---------------------------------------------------------------------------
# Logger (SRP: all output and formatting concerns in one place)
# ---------------------------------------------------------------------------


class Logger(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    _BLUE: ClassVar[str] = "\033[94m"
    _GREEN: ClassVar[str] = "\033[92m"
    _YELLOW: ClassVar[str] = "\033[93m"
    _CYAN: ClassVar[str] = "\033[96m"
    _MAGENTA: ClassVar[str] = "\033[95m"
    _BOLD: ClassVar[str] = "\033[1m"
    _RESET: ClassVar[str] = "\033[0m"

    config: Config

    def _timestamp(self) -> str:
        return datetime.now().strftime("%I:%M:%S %p")

    def startup_banner(self, screen_width: int, screen_height: int) -> None:
        minutes, seconds = divmod(self.config.interval_seconds, 60)
        interval_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
        if seconds:
            interval_str += f" and {seconds} second{'s' if seconds != 1 else ''}"
        print(f"\n{self._BOLD}{self._CYAN}--- MOUSEMOVE STARTING ---{self._RESET}")
        print(f"{self._BOLD}Screen Size:{self._RESET} {screen_width}x{screen_height}")
        print(f"{self._BOLD}Interval:{self._RESET} {interval_str}")
        print(f"{self._YELLOW}To stop: Press Ctrl+C{self._RESET}\n")

    def move_event(self, start_pos: pyautogui.Point, end_pos: pyautogui.Point) -> None:
        ts = self._timestamp()
        print(
            f"[{self._BLUE}{ts}{self._RESET}] "
            f"{self._GREEN}Move:{self._RESET} "
            f"(X: {start_pos.x:4}, Y: {start_pos.y:4}) "
            f"{self._MAGENTA}→{self._RESET} "
            f"(X: {end_pos.x:4}, Y: {end_pos.y:4})"
        )

    def shutdown(self) -> None:
        print(f"\n{self._YELLOW}Goodbye! Mouse mover stopped.{self._RESET}")


# ---------------------------------------------------------------------------
# Orchestrator (SRP: only the run-loop)
# ---------------------------------------------------------------------------


class MouseMover(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    config: Config
    controller: MouseController
    logger: Logger

    def run(self) -> None:
        screen_w, screen_h = self.controller.screen_size()
        max_x, max_y = self.controller.compute_bounds(screen_w, screen_h)
        self.logger.startup_banner(screen_w, screen_h)

        try:
            while True:
                start_pos = self.controller.current_position()
                self.controller.move_to_random(max_x, max_y)
                end_pos = self.controller.current_position()
                self.logger.move_event(start_pos, end_pos)
                time.sleep(self.config.interval_seconds)
        except KeyboardInterrupt:
            self.logger.shutdown()


# ---------------------------------------------------------------------------
# Entrypoint — composition root
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move the mouse periodically to prevent sleep.")
    parser.add_argument(
        "interval",
        nargs="?",
        type=int,
        default=300,
        metavar="SECONDS",
        help="Seconds between moves (default: 300)",
    )
    args = parser.parse_args()
    config = Config(interval_seconds=args.interval)
    MouseMover(
        config=config,
        controller=MouseController(config=config),
        logger=Logger(config=config),
    ).run()
