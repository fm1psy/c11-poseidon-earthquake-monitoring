# 🔧 Earthquake Monitoring Pipeline
This folder is responsible for the pipeline logic used to extract, transform and load earthquake related data. It also contains all the tests that were created in order to verify each part of the pipeline works correctly.
## 📁 Files
| File Name | Description |
| ----------| ----------- |
| **extract.py** | Contains the code that fetches all earthquake data from the past hour, filters the data for earthquakes that happened in the last minute and returns it. |
| **transform.py** | Once the data has been fetched, all unnecessary data is removed and validated. By the end of the transform process, only data with valid values is kept. | 
| **load.py** | This file is responsible for loading data into the database. This includes both earthquake data and new data that wasn't previously in the database such as earthquake monitoring stations. |
| **sns.py** | This runs alongside the pipeline so that all new earthquakes are passed through the notification system. Users who have subscribed to a topic within the radius of a new earthquake will be sent a text and email warning |
| **main.py** | This file contains the entire pipeline process, i.e. running extract, transform and load with the correct arguments. | 
| **handler.py** | Provides the same service as 'main.py' with the only difference being the structure of the file - this file is going to be used as the Lambda function. |
| **test_*.py** | Files starting with 'test_' are used for testing each step of the pipeline. |
| **\*.tf** | Files ending in '.tf' are used to terraform related AWS services, such as the EventBridge scheduler used to run the pipeline every minute. |
| **Dockerfile** | Used to dockerise the pipeline. |
| **requirements.txt** | A list of all the required modules needed to run the pipeline. |

## ❗️❗️ Important
Setup the following environmental variables in a `.env` file:
| Variable Name | Value |
| ------------- | ----- |
| DB_HOST | The public URL of the database. |
| DB_NAME | The name of the database. |
| DB_USERNAME | The username that you will be using to interact with the database. |
| DB_PASSWORD | The password required to interact with the database. |
| DB_PORT | The port the database is listening to. |
| ACCESS_KEY | The unique identifier associated with your AWS account or IAM user.  |
| SECRET_ACCESS_KEY | The 'password' to access your AWS account or IAM user account |

### 💿  Dependencies
There are various folders for each part of the project. In order to run the pipeline, you will need to install the required libraries. This can be done using the code provided below though the terminal:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🏃‍♂️‍➡️ Running the scripts
All the scripts only require basic commands to be executed. Different commands are used depending on the software. Ensure that you are in the dashboard directory before using these commands.
```
# Python running locally
python3 <filename.py>

# Terraform
terraform init
terraform apply
yes

# Docker
docker build -t "image"
docker run --env-file .env -t "image: tag"
```