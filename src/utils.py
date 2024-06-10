"""Project helper functions."""

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
