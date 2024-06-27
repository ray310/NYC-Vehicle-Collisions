"""Tests for utils functions."""

from datetime import datetime
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.strtree import STRtree
import src.utils


def test_date_to_season():
    """Function should work for both datetime and pd.Timestamp objects."""
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


def create_squares(start, end, increment):
    """Return R tree constructed from square shapely geometries and list of ids."""
    shapes = []
    shape_ids = []
    for x in range(start, end, increment):
        y = x
        coords = ((x, y), (x, y + 1), (x + 1, y + 1), (x + 1, y), (x, y))  # square
        shapes.append(Polygon(coords))
        shape_ids.append(str(x))
    rtree = STRtree(shapes)
    return rtree, shape_ids


def test_id_nearest_shape_point_inside():
    """Points inside a shape should return identifier of shape."""
    rtree, shape_ids = create_squares(0, 10, 2)
    inside_points = [Point(x, x) for x in np.arange(0.5, 10, 2)]
    inside_cases = dict(zip(inside_points, shape_ids))
    for k, v in inside_cases.items():
        assert src.utils.id_nearest_shape(k, rtree, shape_ids) == v


def test_id_nearest_shape_point_outside():
    """Points outside a shape should return identifier of nearest shape."""
    rtree, shape_ids = create_squares(0, 10, 2)
    outside_points = [Point(x - 0.1, x - 0.1) for x in np.arange(0, 10, 2)]
    outside_cases = dict(zip(outside_points, shape_ids))
    for k, v in outside_cases.items():
        assert src.utils.id_nearest_shape(k, rtree, shape_ids) == v


def test_id_nearest_shape_point_invalid():
    """Invalid point should return None."""
    rtree, shape_ids = create_squares(0, 10, 2)
    invalid = Point(np.nan, np.nan)
    assert src.utils.id_nearest_shape(invalid, rtree, shape_ids) is None
