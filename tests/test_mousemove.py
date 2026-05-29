import pytest
from unittest.mock import MagicMock, patch

from mousemove import Config, MouseController, Logger, MouseMover


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_config_defaults():
    config = Config()
    assert config.interval_seconds == 300
    assert config.screen_margin == 10
    assert config.move_duration == 0.2
    assert not hasattr(config, "timezone")


def test_config_custom_interval():
    config = Config(interval_seconds=60)
    assert config.interval_seconds == 60


# ---------------------------------------------------------------------------
# MouseController.compute_bounds
# ---------------------------------------------------------------------------


def test_compute_bounds_subtracts_margin():
    config = Config(screen_margin=10)
    controller = MouseController(config=config)
    assert controller.compute_bounds(1920, 1080) == (1910, 1070)


def test_compute_bounds_clamps_to_zero_when_margin_exceeds_screen():
    config = Config(screen_margin=100)
    controller = MouseController(config=config)
    assert controller.compute_bounds(50, 50) == (0, 0)


def test_compute_bounds_no_margin():
    config = Config(screen_margin=0)
    controller = MouseController(config=config)
    assert controller.compute_bounds(1920, 1080) == (1920, 1080)


# ---------------------------------------------------------------------------
# Logger.startup_banner — interval string formatting
# ---------------------------------------------------------------------------


def _banner_output(interval_seconds: int, capsys) -> str:
    config = Config(interval_seconds=interval_seconds)
    Logger(config=config).startup_banner(1920, 1080)
    return capsys.readouterr().out


def test_startup_banner_5_minutes(capsys):
    assert "5 minutes" in _banner_output(300, capsys)


def test_startup_banner_1_minute_singular(capsys):
    out = _banner_output(60, capsys)
    assert "1 minute" in out
    assert "1 minutes" not in out


def test_startup_banner_2_minutes_plural(capsys):
    assert "2 minutes" in _banner_output(120, capsys)


def test_startup_banner_minutes_and_seconds(capsys):
    assert "1 minute and 30 seconds" in _banner_output(90, capsys)


def test_startup_banner_1_second_singular(capsys):
    out = _banner_output(61, capsys)
    assert "1 minute and 1 second" in out
    assert "1 seconds" not in out


def test_startup_banner_plural_minutes_and_plural_seconds(capsys):
    assert "2 minutes and 45 seconds" in _banner_output(165, capsys)


def test_startup_banner_includes_screen_size(capsys):
    out = _banner_output(300, capsys)
    assert "1920x1080" in out


# ---------------------------------------------------------------------------
# MouseMover.run — orchestration
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Logger.move_event and shutdown
# ---------------------------------------------------------------------------


def test_move_event_prints_start_and_end_coordinates(capsys):
    logger = Logger(config=Config())
    start = MagicMock(x=100, y=200)
    end = MagicMock(x=300, y=400)
    logger.move_event(start, end)
    out = capsys.readouterr().out
    assert "100" in out
    assert "200" in out
    assert "300" in out
    assert "400" in out


def test_shutdown_prints_goodbye(capsys):
    Logger(config=Config()).shutdown()
    assert "Goodbye" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# MouseController — real pyautogui delegation
# ---------------------------------------------------------------------------


def test_screen_size_delegates_to_pyautogui():
    with patch("mousemove.pyautogui") as mock_pyautogui:
        mock_pyautogui.size.return_value = (2560, 1440)
        assert MouseController.screen_size() == (2560, 1440)


def test_current_position_delegates_to_pyautogui():
    with patch("mousemove.pyautogui") as mock_pyautogui:
        mock_pos = MagicMock(x=500, y=300)
        mock_pyautogui.position.return_value = mock_pos
        assert MouseController.current_position() == mock_pos


def test_move_to_random_calls_moveto_with_randint_coords_and_duration():
    with patch("mousemove.pyautogui") as mock_pyautogui:
        with patch("mousemove.random.randint", side_effect=[150, 250]):
            config = Config(move_duration=0.5)
            MouseController(config=config).move_to_random(1910, 1070)
            mock_pyautogui.moveTo.assert_called_once_with(150, 250, duration=0.5)


# ---------------------------------------------------------------------------
# MouseMover.run — orchestration
# ---------------------------------------------------------------------------


def _make_mover(config=None):
    config = config or Config()
    controller = MagicMock(spec=MouseController)
    controller.screen_size.return_value = (1920, 1080)
    controller.compute_bounds.return_value = (1910, 1070)
    logger = MagicMock(spec=Logger)
    return MouseMover(config=config, controller=controller, logger=logger)


def test_run_calls_startup_banner_once():
    mover = _make_mover()
    mover.controller.current_position.side_effect = [
        MagicMock(x=100, y=200),
        MagicMock(x=300, y=400),
        KeyboardInterrupt,
    ]
    with patch("mousemove.time.sleep"):
        mover.run()
    mover.logger.startup_banner.assert_called_once_with(1920, 1080)


def test_run_moves_mouse_each_iteration():
    mover = _make_mover()
    mover.controller.current_position.side_effect = [
        MagicMock(x=0, y=0),
        MagicMock(x=500, y=500),
        MagicMock(x=0, y=0),
        MagicMock(x=600, y=600),
        KeyboardInterrupt,
    ]
    with patch("mousemove.time.sleep"):
        mover.run()
    assert mover.controller.move_to_random.call_count == 2


def test_run_logs_move_event_each_iteration():
    mover = _make_mover()
    mover.controller.current_position.side_effect = [
        MagicMock(x=0, y=0),
        MagicMock(x=500, y=500),
        MagicMock(x=0, y=0),
        MagicMock(x=600, y=600),
        KeyboardInterrupt,
    ]
    with patch("mousemove.time.sleep"):
        mover.run()
    assert mover.logger.move_event.call_count == 2


def test_run_sleeps_for_configured_interval():
    config = Config(interval_seconds=42)
    mover = _make_mover(config)
    mover.controller.current_position.side_effect = [
        MagicMock(x=0, y=0),
        MagicMock(x=100, y=100),
        KeyboardInterrupt,
    ]
    with patch("mousemove.time.sleep") as mock_sleep:
        mover.run()
    mock_sleep.assert_called_with(42)


def test_run_calls_shutdown_on_keyboard_interrupt():
    mover = _make_mover()
    mover.controller.current_position.side_effect = KeyboardInterrupt
    with patch("mousemove.time.sleep"):
        mover.run()
    mover.logger.shutdown.assert_called_once()


def test_run_uses_computed_bounds_for_moves():
    mover = _make_mover()
    mover.controller.current_position.side_effect = [
        MagicMock(x=0, y=0),
        MagicMock(x=100, y=100),
        KeyboardInterrupt,
    ]
    with patch("mousemove.time.sleep"):
        mover.run()
    mover.controller.move_to_random.assert_called_once_with(1910, 1070)
