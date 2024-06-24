# Earthquake Monitoring Pipeline
This folder is responsible for the pipeline logic used to extract, transform and load earthquake related data. It also contains all the tests that were created in order to verify each part of the pipeline works correctly.
## Files
| File Name | Description |
| ----------| ----------- |
| **extract.py** | Contains the code that fetches all earthquake data from the past hour, filters the data for earthquakes that happened in the last minute and returns it. |
| **transform.py** | Once the data has been fetched, all unnecessary data is removed and validated. By the end of the transform process, only data with valid values is kept. | 
| **load.py** | This file is responsible for loading data into the database. This includes both earthquake data and new data that wasn't previously in the database such as earthquake monitoring stations. |
| **main.py** | This file contains the entire pipeline process, i.e. running extract, transform and load with the correct arguments. | 
| **handler.py** | Provides the same service as 'main.py' with the only difference being the structure of the file - this file is going to be used as the Lambda function. |
| **test_*.py** | Files starting with 'test_' are used for testing each step of the pipeline. |
| **\*.tf** | Files ending in '.tf' are used to terraform related AWS services, such as the EventBridge scheduler used to run the pipeline every minute. |
| **Dockerfile** | Used to dockerise the pipeline. |
| **requirements.txt** | A list of all the required modules needed to run the pipeline. |
## Instructions for running pipeline
1. Create a virtual environment and download all required modules - assuming you are in the pipeline folder:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2. Setup the following environmental variables in a `.env` file:
    | Variable Name | Value |
    | ------------- | ----- |
    | DB_HOST | The public URL of your database. |
    | DB_USERNAME | The username that you will be using to interact with the database. |
    | DB_PASSWORD | The password required to interact with the database. |
    | DB_PORT | The port the database is listening to. |
3. Run the script using: ```python3 <file_name>```
