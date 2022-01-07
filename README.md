# Analyzing New York City Motor Vehicle Collisions
 
In this project, we analyze motor vehicle collisions in New York City (NYC) to:
- Understand the magnitude of the problem they represent
- Determine when and where collisions occur
- Make it easier to see where serious collisions (collisions with deaths and injuries) are occurring
- Suggest causes and interventions to investigate
- Highlight problematic locations and areas that may not be obvious
<br><br>

### To View Website
completed github-pages link goes here
<br><br>

### To View Notebook Maps
Project notebooks with maps can best be viewed using Jupyter's nbviewer.  
[View project notebooks with nbviewer](https://nbviewer.org/github/ray310/NYC-Vehicle-Collisions/tree/main/) 

_Note that some notebooks may be slow to display or may not display well on mobile devices_
<br><br>

### Data Sources
Collision data and NYPD precinct shapefiles were obtained from NYC OpenData

NYC Collisions <br>
https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95

NYPD Precinct Shapefiles <br>
https://data.cityofnewyork.us/Public-Safety/Police-Precincts/78dh-3ptz
<br><br>

### Reproducing Processed Data and Analysis
1) Download and save data to local directory, e.g. `/data/raw`
2) Create and activate project virtual environment 
   - Python 3.8.12 is used
   - Virtual environment can be created from either
   `conda_environment.yaml` or `requirements.txt`
3) Update data input and output parameters in `process_raw_data.py` as appropriate
4) Run `process_raw_data.py`
5) Run notebooks