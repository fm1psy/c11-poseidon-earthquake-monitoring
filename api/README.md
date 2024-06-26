# Earthquake Monitoring API
This folder contains the codebase to deploy an API, whether locally or online. This API is used to facilitate the retrieval of earthquake data from the relational database.

## Files
| File Name | Purpose |
|-----------|---------|
|`requirements.txt`|Contains all the packages that should be installed for this program to work.|
|`api.py`|Contains the main program that runs the api.|
|`test_api.py`|Contains all the tests developed to verify the api can run correctly.|

## Setup
Before you can run this api, it would be useful to have a database setup; otherwise, you will not be able to connect and pull data from this api. Make sure you have following the instructions in the [database](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/tree/main/database) directory.

## Instructions to deploy the API
Make sure you are inside the api folder before you follow these instructions. 
1. Run the following commands to instantiate a virtual environment. This will enable you to safely install the required packages.
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env ` file within this directory, and make sure the following values are inside it:

| Variable Name | Purpose |
|---------------|---------|
| DB_USERNAME | The username that you will be using to interact with the database. |
| DB_PASSWORD | The password required to interact with the database. |
| DB_HOST | The public URL of the database. |
| DB_PORT | The port the database is listening to. |
| DB_NAME | The name of the database. |

3. Run the script locally using `python api.py`

## Retrieving earthquake data
Once you have the api running, you should be able to connect to the database and retrieve the data accordingly. There is one endpoint, `earthquakes`, that can be accessed through the following:
`URL:port/earthquakes`
This will retrieve every earthquake recorded in the RDS. Below is an example of the expected response:
```
[
  {
    "alert": null,
    "cause_of_event": "earthquake",
    "cdi": null,
    "depth": 8.0,
    "dmin": null,
    "earthquake_id": "ew1719231740",
    "felt": null,
    "gap": null,
    "lat": "38.853900",
    "lon": "-122.844700",
    "magnitude": 4.1,
    "magtype": "mw",
    "mmi": null,
    "network_name": "ew",
    "nst": 4,
    "significance": 259,
    "status": "automatic",
    "time": "Mon, 24 Jun 2024 12:22:22 GMT",
    "title": "M 4.1 - 11 km WNW of Cobb, California"
  }]
```

### Options
Depending on your need for this api, it may be that you wish to retrieve a subset of the earthquake data. There are several options within the `earthquakes` endpoint to facilitate this. These are included using the following format:
`URL:port/earthquakes?[OPTION]=[VALUE]&[OPTION]=[VALUE]`
where `OPTION` is the field you wish to filter the data by, and `VALUE` is the value to filter by. The `&` is optional, and can be used to include multiple options in your data extraction e.g. all earthquakes with a minimum magnitude of 5 within the country of Japan. Below is a table detailing the options available, their purpose, and the current filters accepted.

|Option|Purpose|Accepted Inputs|
|------|-------|---------------|
|[status](https://earthquake.usgs.gov/data/comcat/index.php#status)|Limit data to events with the chosen status|reviewed, automatic, deleted|
|[network](https://earthquake.usgs.gov/data/comcat/index.php#net)|Limit data to events whose contributor matches the chosen ID|ak, at, ci, hv, ld, mb, nc, nm, nn, pr, pt, se, us, uu, uw|
|[alert](https://earthquake.usgs.gov/data/comcat/index.php#alert)|Limit data to events whose level of alert matches the filter|green, yellow, orange, red|
|[mag_type](https://earthquake.usgs.gov/data/comcat/index.php#magType)|Limit data to events whose magnitude was calculated using the chosen method|md, ml, ms, mw, me, mi, mb, mlg|
|[event](https://earthquake.usgs.gov/data/comcat/index.php#type)|Limit data to events whose cause matches the filter|earthquake, quarry blast|
|[min_magnitude](https://earthquake.usgs.gov/data/comcat/index.php#mag)|Limit data to events with magnitudes above the chosen value|Any decimal/integer value. Typically, magnitudes will range from 0-10|
|continent|Limit data to events within the chosen continent|North America, South America, Asia, Africa, Oceania, Europe, Antarctica|
|country|Limit data to events within the chosen country|Any string. Note that if the country does not exist, no data will be returned|