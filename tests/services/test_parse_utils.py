"""Tests for parse_utils module."""

from datetime import timedelta
import pytest
from src.services.parse_utils import parse_time


class TestParseTimeBasic:
    """Basic time parsing functionality."""

    def test_parse_seconds_only(self):
        """Parse plain number as seconds."""
        assert parse_time("90") == timedelta(seconds=90)
        assert parse_time("1") == timedelta(seconds=1)
        assert parse_time("3600") == timedelta(seconds=3600)

    def test_parse_explicit_seconds(self):
        """Parse explicit seconds format (Xs)."""
        assert parse_time("30s") == timedelta(seconds=30)
        assert parse_time("90s") == timedelta(seconds=90)

    def test_parse_minutes(self):
        """Parse minutes format (Xm)."""
        assert parse_time("45m") == timedelta(minutes=45)
        assert parse_time("1m") == timedelta(minutes=1)
        assert parse_time("120m") == timedelta(minutes=120)

    def test_parse_hours(self):
        """Parse hours format (Xh)."""
        assert parse_time("1h") == timedelta(hours=1)
        assert parse_time("2h") == timedelta(hours=2)
        assert parse_time("24h") == timedelta(hours=24)


class TestParseTimeCombinations:
    """Combined time formats."""

    def test_parse_hours_minutes(self):
        """Parse hours and minutes (XhYm)."""
        assert parse_time("1h30m") == timedelta(hours=1, minutes=30)
        assert parse_time("2h15m") == timedelta(hours=2, minutes=15)

    def test_parse_hours_seconds(self):
        """Parse hours and seconds (XhZs)."""
        assert parse_time("1h30s") == timedelta(hours=1, seconds=30)

    def test_parse_minutes_seconds(self):
        """Parse minutes and seconds (YmZs)."""
        assert parse_time("45m30s") == timedelta(minutes=45, seconds=30)
        assert parse_time("1m15s") == timedelta(minutes=1, seconds=15)

    def test_parse_all_components(self):
        """Parse hours, minutes and seconds (XhYmZs)."""
        assert parse_time("1h30m45s") == timedelta(hours=1, minutes=30, seconds=45)
        assert parse_time("2h15m30s") == timedelta(hours=2, minutes=15, seconds=30)


class TestParseTimeCaseInsensitive:
    """Case insensitive parsing."""

    def test_uppercase(self):
        """Parse uppercase format."""
        assert parse_time("45M") == timedelta(minutes=45)
        assert parse_time("1H30M") == timedelta(hours=1, minutes=30)

    def test_mixed_case(self):
        """Parse mixed case format."""
        assert parse_time("1H30m") == timedelta(hours=1, minutes=30)
        assert parse_time("45m30S") == timedelta(minutes=45, seconds=30)


class TestParseTimeErrors:
    """Error handling."""

    def test_invalid_format_raises(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("invalid")

        with pytest.raises(ValueError, match="Invalid time format"):
            parse_time("abc")

    def test_empty_format_raises(self):
        """Empty string raises ValueError."""
        with pytest.raises(ValueError):
            parse_time("")

    def test_only_letters_raises(self):
        """Only unit letters without numbers raises ValueError."""
        with pytest.raises(ValueError):
            parse_time("hms")


class TestParseTimeEdgeCases:
    """Edge cases and special inputs."""

    def test_zero_values(self):
        """Zero values in components are valid."""
        assert parse_time("0h30m") == timedelta(minutes=30)
        assert parse_time("1h0m") == timedelta(hours=1)
        assert parse_time("0s") == timedelta(seconds=0)

    def test_large_values(self):
        """Large values are accepted."""
        assert parse_time("100h") == timedelta(hours=100)
        assert parse_time("999m") == timedelta(minutes=999)
