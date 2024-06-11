""" Script to process raw collision data into analysis-ready dataset"""

import json
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Point
from shapely.strtree import STRtree

# https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
COLLISION_DATA_LOC = "data/raw/Collisions.csv"
PROCESSED_DATA_LOC = "data/processed/crashes.pkl"
NYC_WEST_LIMIT = -74.30  # west of Staten Island
NYC_EAST_LIMIT = -73.70  # east of Queens / Lakeville Rd.
NYC_SOUTH_LIMIT = 40.45  # south of Staten Island
NYC_NORTH_LIMIT = 40.95  # north of the Bronx
POLICE_PRECINCT_GEOMS_LOC = "data/raw/nyc_police_precincts_geoms.geojson"
# https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz
# downloaded June 2024


def id_nearest_shape(point, r_tree, shape_names):
    """Returns the name (from list of shape_names) of the nearest Shapely shape to
    input Shapely point. Uses a Shapely STRtree (R-tree) to perform a faster lookup"""
    name = None
    if point.is_valid:
        name = shape_names[r_tree.nearest(point)]
    return name


# loading downloaded and locally-saved collision data
crashes = pd.read_csv(
    COLLISION_DATA_LOC, dtype={"ZIP CODE": "object"}, low_memory=False
)

# renaming fields
new_col_names = {
    "COLLISION_ID": "ID",
    "CRASH DATE": "DATE",
    "CRASH TIME": "TIME",
    "LATITUDE": "LAT",
    "LONGITUDE": "LONG",
    "NUMBER OF PERSONS INJURED": "INJURED",
    "NUMBER OF PEDESTRIANS INJURED": "PEDESTRIAN INJURED",
    "NUMBER OF CYCLIST INJURED": "CYCLIST INJURED",
    "NUMBER OF PERSONS KILLED": "KILLED",
    "NUMBER OF PEDESTRIANS KILLED": "PEDESTRIAN KILLED",
    "NUMBER OF CYCLIST KILLED": "CYCLIST KILLED",
}
crashes = crashes.rename(columns=new_col_names)

#  Recalculating injured and killed numbers
crashes["INJURED"] = (
    crashes["PEDESTRIAN INJURED"]
    + crashes["CYCLIST INJURED"]
    + crashes["NUMBER OF MOTORIST INJURED"]
)

crashes["KILLED"] = (
    crashes["PEDESTRIAN KILLED"]
    + crashes["CYCLIST KILLED"]
    + crashes["NUMBER OF MOTORIST KILLED"]
)

# selecting the fields to keep
fields_to_keep = [
    "ID",
    "DATE",
    "TIME",
    "LAT",
    "LONG",
    "INJURED",
    "PEDESTRIAN INJURED",
    "CYCLIST INJURED",
    "KILLED",
    "PEDESTRIAN KILLED",
    "CYCLIST KILLED",
]
crashes = crashes[fields_to_keep]

# creating datetime field
dt_fmt = "%m/%d/%Y %H:%M"
crashes["datetime"] = crashes["DATE"] + " " + crashes["TIME"]
crashes["datetime"] = crashes["datetime"].apply(lambda x: datetime.strptime(x, dt_fmt))

# creating season field
season_labels = ["Winter", "Spring", "Summer", "Fall", "Winter"]
season_dates = ["1 Jan", "20 Mar", "20 Jun", "20 Sep", "20 Dec", "31 Dec"]
season_fmt = "%d %b"
season_bins = [
    datetime.strptime(date, season_fmt).timetuple().tm_yday for date in season_dates
]
leap_year_bins = [(x + 1) if x != 1 else x for x in season_bins]
crashes["season"] = pd.cut(
    crashes["datetime"].dt.dayofyear,
    bins=season_bins,
    labels=season_labels,
    include_lowest=True,
    ordered=False,
)

# seasons accounting for leap years
is_leap_year = crashes["datetime"].dt.is_leap_year
crashes.loc[is_leap_year, "season"] = pd.cut(
    crashes["datetime"][is_leap_year].dt.dayofyear,
    bins=leap_year_bins,
    labels=season_labels,
    include_lowest=True,
    ordered=False,
)

# creating  valid location coordinate flags
crashes["valid_lat_long"] = (
    crashes["LONG"].between(NYC_WEST_LIMIT, NYC_EAST_LIMIT)
) & (crashes["LAT"].between(NYC_SOUTH_LIMIT, NYC_NORTH_LIMIT))

# creating collision flags
crashes["serious"] = (crashes["INJURED"] > 0) | (crashes["KILLED"] > 0)
crashes["non-motorist"] = (
    (crashes["PEDESTRIAN INJURED"] > 0)
    | (crashes["CYCLIST INJURED"] > 0)
    | (crashes["PEDESTRIAN KILLED"] > 0)
    | (crashes["CYCLIST KILLED"] > 0)
)

# creating GeoDataFrame with Shapely Point corresponding to lat-long coordinates
points = [Point(x, y) for x, y in zip(crashes["LONG"].array, crashes["LAT"].array)]
crashes = gpd.GeoDataFrame(crashes, geometry=points)
# gpd.points_from_xy() not used to create GeoDataFrame due to it
# throwing Shapely deprecation warning


# assigning NYC police precinct to collision based on location
with open(
    POLICE_PRECINCT_GEOMS_LOC, encoding="utf-8"
) as fp:  # downloaded and locally-saved
    police_geojson = json.load(fp)
precinct_geos = [shape(x["geometry"]) for x in police_geojson["features"]]
precinct_nums = [x["properties"]["precinct"] for x in police_geojson["features"]]
precinct_tree = STRtree(precinct_geos)
crashes.loc[crashes["valid_lat_long"], "precinct"] = crashes.apply(
    lambda x: id_nearest_shape(x.geometry, precinct_tree, precinct_nums), axis=1
)

# save processed data
crashes.to_pickle(PROCESSED_DATA_LOC)
