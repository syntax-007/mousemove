"""
Tests for mousemove.py.

Unit tests for extracted helper functions are written RED-first:
they fail until compute_bounds / get_timestamp / format_move_log are
extracted from move_mouse_periodically.

Integration tests characterise the existing end-to-end behaviour and
must pass both before and after the refactor.
"""
import re
import pytest
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo


# ── Unit tests (RED until functions are extracted) ─────────────────────────────

class TestComputeBounds:
    def test_standard_1080p_screen(self):
        from mousemove import compute_bounds
        assert compute_bounds(1920, 1080) == (1910, 1070)

    def test_smaller_screen(self):
        from mousemove import compute_bounds
        assert compute_bounds(800, 600) == (790, 590)

    def test_4k_screen(self):
        from mousemove import compute_bounds
        assert compute_bounds(3840, 2160) == (3830, 2150)

    def test_screen_exactly_at_margin_clamps_to_zero(self):
        from mousemove import compute_bounds
        assert compute_bounds(10, 10) == (0, 0)

    def test_screen_smaller_than_margin_clamps_to_zero(self):
        from mousemove import compute_bounds
        assert compute_bounds(5, 3) == (0, 0)

    def test_zero_dimensions_clamp_to_zero(self):
        from mousemove import compute_bounds
        assert compute_bounds(0, 0) == (0, 0)

    def test_asymmetric_dimensions(self):
        from mousemove import compute_bounds
        assert compute_bounds(1280, 8) == (1270, 0)


class TestGetTimestamp:
    def test_returns_a_string(self):
        from mousemove import get_timestamp
        result = get_timestamp(ZoneInfo("US/Central"))
        assert isinstance(result, str)

    def test_matches_12h_time_format(self):
        from mousemove import get_timestamp
        result = get_timestamp(ZoneInfo("US/Central"))
        assert re.search(r'\d{2}:\d{2}:\d{2} [AP]M', result), (
            f"Expected HH:MM:SS AM/PM format, got: {result!r}"
        )

    def test_respects_given_timezone(self):
        """Timestamp must use the timezone passed in, not a hardcoded one."""
        from mousemove import get_timestamp
        from unittest.mock import patch
        from datetime import datetime, timezone, timedelta
        fixed_dt = datetime(2024, 6, 15, 14, 30, 45, tzinfo=timezone.utc)
        with patch('mousemove.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_dt.astimezone(ZoneInfo("US/Central"))
            mock_dt.now.side_effect = lambda tz: fixed_dt.astimezone(tz)
            result = get_timestamp(ZoneInfo("UTC"))
        assert "02:30:45 PM" in result


class TestFormatMoveLog:
    def test_contains_timestamp(self):
        from mousemove import format_move_log
        result = format_move_log("01:23:45 PM", MagicMock(x=0, y=0), MagicMock(x=0, y=0))
        assert "01:23:45 PM" in result

    def test_contains_start_x(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=111, y=0), MagicMock(x=0, y=0))
        assert "111" in result

    def test_contains_start_y(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=0, y=222), MagicMock(x=0, y=0))
        assert "222" in result

    def test_contains_end_x(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=0, y=0), MagicMock(x=333, y=0))
        assert "333" in result

    def test_contains_end_y(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=0, y=0), MagicMock(x=0, y=444))
        assert "444" in result

    def test_contains_unicode_arrow(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=0, y=0), MagicMock(x=0, y=0))
        assert "→" in result

    def test_is_a_string(self):
        from mousemove import format_move_log
        result = format_move_log("12:00:00 PM", MagicMock(x=0, y=0), MagicMock(x=0, y=0))
        assert isinstance(result, str)


# ── Integration tests (must pass before AND after refactor) ───────────────────

def _patched_run(interval=5, screen_size=(1920, 1080), stop_on_sleep=True):
    """Run move_mouse_periodically through exactly one move cycle, then stop."""
    import mousemove
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)
        raise KeyboardInterrupt

    ctx_sleep = patch('mousemove.time.sleep', side_effect=fake_sleep)
    ctx_pg = patch('mousemove.pyautogui')

    with ctx_pg as mock_pg, ctx_sleep:
        mock_pg.size.return_value = screen_size
        mock_pg.position.return_value = MagicMock(x=50, y=60)
        mousemove.move_mouse_periodically(interval)
        return mock_pg, sleep_calls


class TestStartupBanner:
    def test_shows_screen_width(self, capsys):
        _patched_run(screen_size=(1920, 1080))
        assert "1920" in capsys.readouterr().out

    def test_shows_screen_height(self, capsys):
        _patched_run(screen_size=(1920, 1080))
        assert "1080" in capsys.readouterr().out

    def test_shows_interval(self, capsys):
        _patched_run(interval=42)
        assert "42" in capsys.readouterr().out

    def test_shows_timezone_key(self, capsys):
        _patched_run()
        assert "US/Central" in capsys.readouterr().out


class TestMoveLoop:
    def test_x_coordinate_within_bounds(self):
        xs = []

        def capture_move(x, y, duration):
            xs.append(x)
            if len(xs) >= 5:
                raise KeyboardInterrupt

        import mousemove
        with patch('mousemove.pyautogui') as mock_pg, patch('mousemove.time.sleep'):
            mock_pg.size.return_value = (1920, 1080)
            mock_pg.position.return_value = MagicMock(x=0, y=0)
            mock_pg.moveTo.side_effect = capture_move
            mousemove.move_mouse_periodically(5)

        for x in xs:
            assert 0 <= x <= 1910, f"x={x} out of [0, 1910]"

    def test_y_coordinate_within_bounds(self):
        ys = []

        def capture_move(x, y, duration):
            ys.append(y)
            if len(ys) >= 5:
                raise KeyboardInterrupt

        import mousemove
        with patch('mousemove.pyautogui') as mock_pg, patch('mousemove.time.sleep'):
            mock_pg.size.return_value = (1920, 1080)
            mock_pg.position.return_value = MagicMock(x=0, y=0)
            mock_pg.moveTo.side_effect = capture_move
            mousemove.move_mouse_periodically(5)

        for y in ys:
            assert 0 <= y <= 1070, f"y={y} out of [0, 1070]"

    def test_move_duration_is_0_2(self):
        durations = []

        def capture_move(x, y, duration):
            durations.append(duration)
            raise KeyboardInterrupt

        import mousemove
        with patch('mousemove.pyautogui') as mock_pg, patch('mousemove.time.sleep'):
            mock_pg.size.return_value = (1920, 1080)
            mock_pg.position.return_value = MagicMock(x=0, y=0)
            mock_pg.moveTo.side_effect = capture_move
            mousemove.move_mouse_periodically(5)

        assert durations == [0.2]

    def test_sleeps_for_given_interval(self):
        _, sleep_calls = _patched_run(interval=99)
        assert sleep_calls == [99]

    def test_tiny_screen_moves_to_origin(self):
        move_args = []

        def capture_move(x, y, duration):
            move_args.append((x, y))
            raise KeyboardInterrupt

        import mousemove
        with patch('mousemove.pyautogui') as mock_pg, patch('mousemove.time.sleep'):
            mock_pg.size.return_value = (5, 5)
            mock_pg.position.return_value = MagicMock(x=0, y=0)
            mock_pg.moveTo.side_effect = capture_move
            mousemove.move_mouse_periodically(5)

        assert move_args == [(0, 0)]

    def test_log_shows_start_position(self, capsys):
        import mousemove
        call_n = [0]

        def fake_pos():
            call_n[0] += 1
            return MagicMock(x=111, y=222) if call_n[0] == 1 else MagicMock(x=0, y=0)

        with patch('mousemove.pyautogui') as mock_pg, \
             patch('mousemove.time.sleep', side_effect=KeyboardInterrupt):
            mock_pg.size.return_value = (1920, 1080)
            mock_pg.position.side_effect = fake_pos
            mousemove.move_mouse_periodically(5)

        out = capsys.readouterr().out
        assert "111" in out
        assert "222" in out

    def test_log_shows_end_position(self, capsys):
        import mousemove
        call_n = [0]

        def fake_pos():
            call_n[0] += 1
            return MagicMock(x=0, y=0) if call_n[0] == 1 else MagicMock(x=333, y=444)

        with patch('mousemove.pyautogui') as mock_pg, \
             patch('mousemove.time.sleep', side_effect=KeyboardInterrupt):
            mock_pg.size.return_value = (1920, 1080)
            mock_pg.position.side_effect = fake_pos
            mousemove.move_mouse_periodically(5)

        out = capsys.readouterr().out
        assert "333" in out
        assert "444" in out


class TestKeyboardInterrupt:
    def test_prints_stopped_message(self, capsys):
        _patched_run()
        assert "stopped" in capsys.readouterr().out.lower()

    def test_does_not_propagate_exception(self):
        # move_mouse_periodically must return cleanly on KeyboardInterrupt
        _patched_run()  # would raise if not handled
