"""Project helper functions."""

import bisect
import calendar
import datetime
import json
import geopandas as gpd
import pandas as pd
import shapely
from shapely.geometry import shape
from shapely.strtree import STRtree


def make_week_crosstab(df, divisor, values=None, aggfunc=None, day_of_week_map=None):
    """Return an hour / day-of-week crosstab scaled by a divisor."""
    ct = pd.crosstab(
        index=df["datetime"].dt.dayofweek,
        columns=df["datetime"].dt.hour,
        values=values,
        aggfunc=aggfunc,
    )
    if day_of_week_map:
        ct.rename(index=day_of_week_map, inplace=True)
    ct /= divisor  # scale crosstab by divisor
    return ct


def get_crosstab_min_max(
    df, col, categories, divisor=None, values_col=None, aggfunc=None
):
    """Return the min and max values of weekly crosstabs across all categories.

    Categories should be an iterable. Used to ensure that different heatmaps
    have the same scale.
    """
    max_val = float("-inf")
    min_val = float("inf")
    for cat in categories:
        is_true = df[col].isin([cat])
        idx = df.loc[is_true, "datetime"].dt.dayofweek
        cols = df.loc[is_true, "datetime"].dt.hour
        values = None
        if aggfunc:
            values = df.loc[is_true, values_col]
        ct = pd.crosstab(index=idx, columns=cols, values=values, aggfunc=aggfunc)

        min_val = min(min_val, min(ct.min()))  # ct.min() returns pd.Series
        max_val = max(max_val, max(ct.max()))
    if divisor:
        min_val /= divisor
        max_val /= divisor
    return min_val, max_val


def make_heatmap_labels(
    title, x_label="Hour of Day", y_label="", cbar_label="Number of Collisions per Hour"
):
    """Return a dictionary of labels for a 2D heatmap."""
    ct_labels = {
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "cbar_label": cbar_label,
    }
    return ct_labels


def date_to_season(dt: datetime.datetime):
    """Convert individual datetime or pd.Timestamp to season of year."""
    # day of year corresponding to following dates:
    # 1-Jan, 21-Mar, 21-Jun, 21-Sep, 21-Dec, 31-Dec
    # day of year can be obtained using datetime_obj.timetuple().tm_yday
    # 21-March is considered first day of Spring, etc.
    season_bins = (1, 80, 172, 264, 355, 365)
    leap_year_season_bins = (1, 81, 173, 265, 356, 366)
    season_labels = ("Winter", "Spring", "Summer", "Fall", "Winter")

    bins = season_bins
    if calendar.isleap(dt.year):
        bins = leap_year_season_bins
    idx = (bisect.bisect(bins, dt.timetuple().tm_yday) - 1) % len(season_labels)
    return season_labels[idx]


def read_geojson(shape_file_loc: str, property_name: str):
    """
    Return list of geometry ids and list of geometries from geojson.

    Assumes geojson conforms to 2016 geojson convention.
    """
    with open(shape_file_loc, encoding="utf-8") as fp:
        geojson = json.load(fp)
    geom_ids = [x["properties"][property_name] for x in geojson["features"]]
    geoms = [shape(x["geometry"]) for x in geojson["features"]]
    return geom_ids, geoms


def id_nearest_shape(geometry: shapely.Point, r_tree: shapely.STRtree, shape_ids: list):
    """
    Return the id (from list of shape_ids) of the nearest shape to input geometry.

    Uses a Shapely STRtree (R-tree) to perform a faster lookup.
    """
    sid = None
    if shapely.is_valid(geometry) and not shapely.is_empty(geometry):
        sid = shape_ids[r_tree.nearest(geometry)]
    return sid


def add_location_feature(
    gdf: gpd.GeoDataFrame,
    geojson_path: str,
    geojson_property: str,
    feature_name: str = None,
):
    """Return a GeoPandas.Dataframe with added location-related feature.

    Feature value is set to identifier of the nearest geometry in the read geojson.
    """
    geom_ids, geoms = read_geojson(geojson_path, geojson_property)
    tree = STRtree(geoms)
    if not feature_name:
        feature_name = geojson_property
    gdf[feature_name] = gdf.apply(
        lambda x: id_nearest_shape(x.geometry, tree, geom_ids), axis=1
    )
    return gdf
