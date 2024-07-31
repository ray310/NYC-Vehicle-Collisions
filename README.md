# Analyzing New York City Motor Vehicle Collisions
#### [https://ray310.github.io/NYC-Vehicle-Collisions/](https://ray310.github.io/NYC-Vehicle-Collisions/)

In this project, we analyze motor vehicle collisions in New York City (NYC) to:
- Understand the magnitude of the problem they represent
- Determine when and where collisions occur
- Evaluate when collisions are elevated relative to traffic levels
- Make it easier to see where serious collisions (collisions with deaths and injuries) are occurring
- Suggest causes and interventions to investigate
- Highlight problematic locations and areas that may not be obvious
<br><br>

### To View Project Website
[https://ray310.github.io/NYC-Vehicle-Collisions/](https://ray310.github.io/NYC-Vehicle-Collisions/)
<br><br>

### Supplemental Analysis
__Vehicle Activity Index__

- The vehicle activity index is constructed to identify when collisions are
 elevated relative to the level of driving.
- The index is based on traffic volumes in the Metropolitan
 Transit Authority (MTA) Bridge and Tunnel dataset.
- Yearly, monthly, weekly, and daily traffic patterns in the MTA dataset were profiled
- Relationships between toll crossings was evaluated using cross-correlation and
 by examining the weekly traffic pattern of select crossings.
 patterns was performed
- Gaps were identified in the MTA dataset and imputed using XGBoost regression.
- Please see the following notebooks:
  - [1b-profiling-mta-traffic-index.ipynb](https://nbviewer.org/github/ray310/NYC-Vehicle-Collisions/blob/main/1b-profiling-mta-traffic-index.ipynb)
  - [2a-preparing-mta-data-xgboost.ipynb](https://nbviewer.org/github/ray310/NYC-Vehicle-Collisions/blob/main/2a-preparing-mta-data-xgboost.ipynb)

__Cycling Activity Index__

- The cycling activity index is constructed to identify when collisions with cyclists
 are elevated relative to the level of cycling.
- The index is based on cycling volumes at several bicycle counters throughout NYC in
 the NYC Bicycle Counts dataset
- The 30+ bicycle counters were reviewed for completeness of data
- The index was constructed using a composite of counters to provide a consistent index
 going back to 2015
- Yearly, monthly, weekly, and daily traffic patterns in the cycling index were profiled
- Please see the following notebooks:
  - [1c-profiling-nyc-bike-counter-data.ipynb](https://nbviewer.org/github/ray310/NYC-Vehicle-Collisions/blob/main/1c-profiling-nyc-bike-counter-data.ipynb)

### To Directly View Notebooks with Full Content
Project notebooks with maps can best be viewed using Jupyter's nbviewer.  
[View project notebooks with nbviewer](https://nbviewer.org/github/ray310/NYC-Vehicle-Collisions/tree/main/)

_Note that some notebooks may be slow to display or may not display well on mobile devices_
<br><br>

### Data Sources
NYC Collisions <br>
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95

NYPD Precinct Shapefiles <br>
https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz

MTA Bridge and Tunnel Toll Data <br>
https://data.ny.gov/Transportation/Hourly-Traffic-on-Metropolitan-Transportation-Auth/qzve-kjga/about_data

NYC Bicycle Counts <br>
https://data.cityofnewyork.us/Transportation/Bicycle-Counts/uczf-rk3c/about_data

NYC Bicycle Counters <br>
https://data.cityofnewyork.us/Transportation/Bicycle-Counters/smn3-rzf9/about_data

NYC City Council District Shapefiles <br>
https://data.cityofnewyork.us/City-Government/City-Council-Districts/yusd-j4xi
<br><br>

### Reproducing Processed Data and Analysis
1) Clone repo
2) Download and save data to local directory, e.g. `/data/raw`
3) Create and activate project virtual environment
   - Python 3.12.3 is used
   - Virtual environment can be created from either
   `conda_environment.yaml` or `requirements.txt`
4) Update data input and output parameters in `process_raw_data.py` as appropriate
5) Run `process_raw_data.py` (this script may take a while)
6) To obtain City Council point of contact information, run `src/scrape_city_council.py` with required command line arguments
7) Run notebooks
