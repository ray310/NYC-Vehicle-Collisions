"""Module to process raw collision data into analysis-ready dataset."""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

import src.utils
from src.constants import (
    NYC_WEST_LIMIT,
    NYC_EAST_LIMIT,
    NYC_SOUTH_LIMIT,
    NYC_NORTH_LIMIT,
)

PROCESSED_DATA_LOC = "data/processed/crashes.pkl"

# downloaded June 2024
# https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
COLLISION_DATA_LOC = "data/raw/collisions/Collisions.csv"

# downloaded June 2024
# https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz
POLICE_PRECINCT_GEOMS_LOC = "data/raw/police/nyc_police_precincts_geoms.geojson"

# downloaded June 2024
# https://data.cityofnewyork.us/City-Government/City-Council-Districts/yusd-j4xi
DISTRICT_GEO_LOC = "data/raw/citycouncil/City Council Districts.geojson"


def process_data():
    """Script to process raw collision data into analysis-ready dataset."""
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

    # creating datetime index
    dt_str = crashes["DATE"] + " " + crashes["TIME"]
    crashes["datetime"] = pd.to_datetime(dt_str, format="%m/%d/%Y %H:%M")
    crashes = crashes.set_index("datetime")

    # creating season field
    crashes["season"] = pd.Categorical(crashes.index.map(src.utils.date_to_season))

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
    crashes["cyclist"] = (crashes["CYCLIST INJURED"] > 0) | (
        crashes["CYCLIST KILLED"] > 0
    )
    crashes["pedestrian"] = (crashes["PEDESTRIAN INJURED"] > 0) | (
        crashes["PEDESTRIAN KILLED"] > 0
    )

    # creating GeoDataFrame with Shapely Point corresponding to lat-long coordinates
    # empty lat-longs (np.nan) will be represented in GeoDataFrame as empty Point()
    points = [Point(x, y) for x, y in zip(crashes["LONG"].array, crashes["LAT"].array)]
    crashes = gpd.GeoDataFrame(crashes, geometry=points)
    crashes = src.utils.add_location_feature(
        crashes, POLICE_PRECINCT_GEOMS_LOC, "precinct"
    )
    crashes["precinct"] = pd.Categorical(crashes["precinct"])
    crashes = src.utils.add_location_feature(
        crashes, DISTRICT_GEO_LOC, "coun_dist", feature_name="district"
    )
    crashes["district"] = pd.Categorical(crashes["district"])

    # save processed data
    crashes.to_pickle(PROCESSED_DATA_LOC)


if __name__ == "__main__":
    process_data()
