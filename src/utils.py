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
