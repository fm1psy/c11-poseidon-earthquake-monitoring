# 📊 Dashboard
This folder is responsible for the pipeline logic used to extract, transform and load earthquake related data. It also contains all the tests that were created in order to verify each part of the pipeline works correctly.
## 📁 Files
| File Name | Description |
| ----------| ----------- |
| **charts.py** | Contains all charts which are being used on the dashboard |
| **notifications.py** | Contains script for users to subscribe for notification alerts for earthquakes |
| **weekly_report.py** | Contains functions to allow users to be able to download weekly reports |
| **main.py** | This file contains the entire dashboard, including the functionality e.g. adjusting time frame of displayed earthquakes on map | 
| **\*.tf** | Files ending in '.tf' are used to terraform related AWS services, such as the ECS service used to host the dashboard |
| **Dockerfile** | Used to dockerise the dashboard. |
| **requirements.txt** | A list of all the required modules needed to run the dashboard. |

## ❗️❗️ Important
Setup the following environmental variables in a `.env` file:
| Variable Name | Value |
| ------------- | ----- |
| DB_HOST | The public URL of the database. |
| DB_NAME | The name of the database. |
| DB_USERNAME | The username that you will be using to interact with the database. |
| DB_PASSWORD | The password required to interact with the database. |
| DB_PORT | The port the database is listening to. |


### 💿  Dependencies
There are various folders for each part of the project. In order to run the dashboard, you will need to install the required libraries. This can be done using the code provided below though the terminal:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 🏃‍♂️‍➡️ Running the scripts
All the scripts only require basic commands to be executed. Different commands are used depending on the software. Ensure that you are in the dashboard directory before using these commands.
```
# Python running locally
streamlit run main.py

# Terraform
terraform init
terraform apply
yes

# Docker
docker build -t "image"
docker run --env-file .env -t "image: tag"
```