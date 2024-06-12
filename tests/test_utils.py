"""Tests for utils functions."""

import pytest
from datetime import datetime
import pandas as pd
import src.utils


def test_date_to_season():
    """ Function should work for both datetime and pd.Timestamp objects"""
    test_cases = {
        datetime(year=1900, month=1, day=1): "Winter",
        pd.Timestamp(year=1900, month=1, day=1): "Winter",
        datetime(year=1900, month=3, day=20): "Winter",
        pd.Timestamp(year=1900, month=3, day=20): "Winter",
        datetime(year=1900, month=3, day=21): "Spring",
        pd.Timestamp(year=1900, month=3, day=21): "Spring",
        datetime(year=2000, month=3, day=20): "Winter",  # leap year
        pd.Timestamp(year=2000, month=3, day=20): "Winter",  # leap year
        datetime(year=2000, month=3, day=21): "Spring",  # leap year
        pd.Timestamp(year=2000, month=3, day=21): "Spring",  # leap year
        datetime(year=1900, month=6, day=20): "Spring",
        pd.Timestamp(year=1900, month=6, day=20): "Spring",
        datetime(year=1900, month=6, day=21): "Summer",
        pd.Timestamp(year=1900, month=6, day=21): "Summer",
        datetime(year=1900, month=9, day=20): "Summer",
        pd.Timestamp(year=1900, month=9, day=20): "Summer",
        datetime(year=1900, month=9, day=21): "Fall",
        pd.Timestamp(year=1900, month=9, day=21): "Fall",
        datetime(year=1900, month=12, day=20): "Fall",
        pd.Timestamp(year=1900, month=12, day=20): "Fall",
        datetime(year=1900, month=12, day=21): "Winter",
        pd.Timestamp(year=1900, month=12, day=21): "Winter",
        datetime(year=1900, month=12, day=31): "Winter",
        pd.Timestamp(year=1900, month=12, day=31): "Winter",
    }
    for k, v in test_cases.items():
        assert src.utils.date_to_season(k) == v
