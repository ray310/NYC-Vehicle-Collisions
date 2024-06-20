"""Project helper functions."""

import bisect
import calendar
import datetime
import pandas as pd


def make_week_crosstab(df, divisor, values=None, aggfunc=None, day_of_week_map=None):
    """Returns an hour / day-of-week crosstab scaled by a divisor."""
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


def get_crosstab_min_max(df, col, categories, divisor=None):
    """Returns the absolute min and absolute max values of weekly crosstabs across
    all categories. Used to ensure that different heatmaps have the same scale."""
    max_val = float("-inf")
    min_val = float("inf")
    for cat in categories:
        is_true = df[col].isin([cat])
        idx = df.loc[is_true, "datetime"].dt.dayofweek
        cols = df.loc[is_true, "datetime"].dt.hour
        ct = pd.crosstab(index=idx, columns=cols)

        min_val = min(min_val, min(ct.min()))  # ct.min() returns pd.Series
        max_val = max(max_val, max(ct.max()))
    if divisor:
        min_val /= divisor
        max_val /= divisor
    return min_val, max_val


def make_heatmap_labels(
    title, x_label="Hour of Day", y_label="", cbar_label="Number of Collisions per Hour"
):
    """Returns a dictionary of labels for a 2D heatmap."""
    ct_labels = {
        "title": title,
        "x_label": x_label,
        "y_label": y_label,
        "cbar_label": cbar_label,
    }
    return ct_labels


def date_to_season(dt: datetime.datetime):
    """Converts individual datetime or pd.Timestamp to season of year"""
    # day of year corresponding to following dates:
    # 1-Jan, 21-Mar, 21-Jun, 21-Sep, 21-Dec, 31-Dec
    # day of year can be obtained using datetime_obj.timetuple().tm_yday
    # 21-March is considered first day of Spring, etc.
    SEASON_BINS = (1, 80, 172, 264, 355, 365)
    LEAP_YEAR_SEASON_BINS = (1, 81, 173, 265, 356, 366)
    SEASON_LABELS = ("Winter", "Spring", "Summer", "Fall", "Winter")

    season_bins = SEASON_BINS
    if calendar.isleap(dt.year):
        season_bins = LEAP_YEAR_SEASON_BINS
    idx = (bisect.bisect(season_bins, dt.timetuple().tm_yday) - 1) % len(SEASON_LABELS)
    return SEASON_LABELS[idx]
