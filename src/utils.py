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
from sklearn import model_selection


def min_max_across_crosstabs(
    categories, cat_series, idx_series, col_series, value_series=None, aggfunc=None
):
    """Return the min and max values of crosstabs across all categories.

    Categories should be an iterable. Used to ensure that different heatmaps
    have the same scale.
    """
    if value_series is not None and aggfunc is None:
        raise TypeError("'value_series' requires 'aggfunc' to be specified.")
    max_val = float("-inf")
    min_val = float("inf")
    for cat in categories:
        is_true = cat_series.isin([cat])
        idx = idx_series[is_true]
        cols = col_series[is_true]
        values = None
        if aggfunc:
            values = value_series[is_true]
        ct = pd.crosstab(index=idx, columns=cols, values=values, aggfunc=aggfunc)

        min_val = min(min_val, min(ct.min()))  # ct.min() / max() return pd.Series
        max_val = max(max_val, max(ct.max()))
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


def date_to_season(dt: datetime.datetime | pd.Timestamp):
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
    """Return list of geometry ids and list of geometries from geojson.

    Assumes geojson conforms to 2016 geojson convention.
    """
    with open(shape_file_loc, encoding="utf-8") as fp:
        geojson = json.load(fp)
    geom_ids = [x["properties"][property_name] for x in geojson["features"]]
    geoms = [shape(x["geometry"]) for x in geojson["features"]]
    return geom_ids, geoms


def id_nearest_shape(geometry: shapely.Point, r_tree: shapely.STRtree, shape_ids: list):
    """Return the id (from list of shape_ids) of the nearest shape to input geometry.

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


def search_grid(x, y, model, params, score, num_cv=5, low_score_best=True):
    """Perform grid search cross validation then print and return results.

    Args:
        x (pd.DataFrame, pd.Series, or np.ndarray): Model features.
        y (pd.Series, or np.ndarray): Target.
        model (sklearn model): Model to use in grid search.
        params (dict): Key-value parameters to use in grid search. Key is model
            input name.
        score (str, callable, list, tuple or dict): Strategy to evaluate the
            performance of the cross-validated model on the test set.
        num_cv (int, cv generator or  iterable): CV splitting strategy.
        low_score_best (bool): Whether the lowest score is best. False indicates
            that the highest score is best score.

    Returns:
        list(tup): List of grid search cross-validation results as tuples containing:
            1) mean test score
            2) run time in minutes
            3) parameters used

    """
    param_grid = model_selection.ParameterGrid(params)
    results = []
    print("Mean Score", "\tRun Time(min)", "\tParameters")
    for param in param_grid:
        parameterized_model = model(**param)
        cv_run = model_selection.cross_validate(
            parameterized_model, x, y, scoring=score, cv=num_cv
        )

        mean_score = sum(cv_run["test_score"]) / num_cv
        minutes = (sum(cv_run["fit_time"]) + sum(cv_run["score_time"])) / 60
        results.append((mean_score, minutes, param))
        result_string = f"{mean_score:.4f}\t\t{minutes:.3f}\t\t{param}"
        print(result_string)

    results.sort(key=lambda z: z[0], reverse=low_score_best)
    best_score = f"\nBest score: {results[0][0]}\n"
    best_params = f"Best parameters: {results[0][2]}\n"
    print(best_score + best_params)

    return results
