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