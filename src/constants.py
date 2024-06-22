""" Project constants, parameters, and settings."""

COORD_REF_SYSTEM = "EPSG:4326"  # default geojson CRS

DAY_OF_WEEK_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

MONTHS_MAP = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

NYC_MAP_CENTER = (40.73, -73.92)
NYC_NORTH_LIMIT = 40.95  # north of the Bronx
NYC_EAST_LIMIT = -73.70  # east of Queens / Lakeville Rd.
NYC_SOUTH_LIMIT = 40.45  # south of Staten Island
NYC_WEST_LIMIT = -74.30  # west of Staten Island

SEASONS = ("Winter", "Spring", "Summer", "Fall")
