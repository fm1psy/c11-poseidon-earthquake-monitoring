# 🌎 c11-poseidon-earthquake-monitoring

This project will monitor the United States Geological Survey (USGS) earthquake data feeds, continually extracting and storing data. This data will be used to provide interactive dashboards  and subscribable alerts, so that users can make appropriate preparations/decisions with full knowledge of earthquake risks.

## 🗄️ Folders

| Folder Name | Description |
|---|---|
| **.github** | Essential files for your GitHub repository. |
| **api** | An API to allow developers to query earthquake data. |
| **dashboard**  | A file which contains scipts to host the dashboard, pdf reports and earthquake alert sign up form. |
| **database** | A PostgreSQL database to store all the real-time earthquake data. |
| **diagrams**  | Images that map out the project for easy understanding. |
| **pipeline**  | Code that brings data from the QuakeML API to the database. Also includes script for SNS warnings in the event of an earthquake. |
| **weekly-report**  | A summary report which contains information gathered on earthquakes in the past week. |



## 📐 Architecture Design

For a visual representation of the project architecture and details on the design decisions, please refer to this section.

### ☁️ Cloud Resources
For this project, we have designed it with the intention of hosting everything on the cloud in order to automate it. The python scripts can still be ran locally but the terraform scripts have been included within the repository if you desire to host this system on the cloud as well. The cloud service that has been used is **AWS**.

### 📐 Architecture Diagram

![Architecture Diagram](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/blob/main/diagrams/architecture_diagram.png)

### ✏️ Design Decisions

#### PDF Report Generator
Reports are generated inside a lambda function and are stored in the S3 bucket “report storage bucket”. This function is triggered once every week, which is enough data for a valuable summary to be generated, such as average magnitude and depth.
Users that wish to access a weekly report can do so through the dashboard, as we plan to have a page dedicated to this. This allows us to create a service that gives users the ability to access reports not just from this week, but from previous ones too.
#### Earthquake Dashboard Service
This dashboard service reads from the postgres Relational Database (RDS) to display key statistics regarding the data available (mean values, significant earthquakes, etc.). Because we want this service to be available at all times, we are choosing to run it as an Elastic Container Service (ECS). It also reads from an S3 bucket which contains every weekly report since the genesis of this system, so as to provide users with a downloadable PDF for every week.
#### Earthquake User API Service
This is run as an ECS, where the API is hosted by a Fargate instance, as the API is a constantly running service
#### ETL Pipeline with Email Alert
This pipeline is run as a lambda function, since it is expected to only run for at most a minute, and lambda has the capacity to expand horizontally if need be. It is triggered by an event scheduler every minute, since that is how often the data in the USGS QuakeML is updated. It then processes the data extracted and writes it to the RDS. It will also send an alert via SNS to those that have subscribed to it.

## 📏 Database Design

For a visual representation of the database schema and details on the design decisions, please refer to this section.

### 🪧 Entity-Relationship Diagram (ERD)

The provided Entity-Relationship Diagram (ERD) illustrates a database schema designed for tracking earthquake data. The schema follows the principles of Third Normal Form (3NF). There is a main earthquake table that captures data specific to each earthquake event. Additionally, lookup tables are included for categories such as status, alerts and networks.

![ERD Diagram](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/blob/main/diagrams/erd_diagram.png)


## ✅ Getting Setup

The sections below detail all the instructions to get this project running.

### 💿 Installations
The following languages/softwares are required for this project. Things assigned as optional are only required if you desire to host this system on the cloud.
- Python
- Bash
- Terraform (Optional)
- Docker (Optional)

### ❗️ Dependencies

1. **Clone the repository**:
    ```bash
    git clone https://github.com/danfh00/vodnik-plant-health-monitor.git
    ```

2. **Create and activate a virtual environment (optional but recommended)**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## 📗 Authors

| Name | Github Profile |
|---|---|
| **Ella Jepsen** | **[ejepsen88](https://github.com/ejepsen88)**|
| **Freddy Martinez Rosero** | **[fm1psy](https://github.com/fm1psy)**|
| **Joe Lam** | **[joe1606](https://github.com/joe1606)** |
| **Umar Haider** | **[laUmar123](https://github.com/laUmar123)** |
| **Will Banks** | **[WillBanks1](https://github.com/WillBanks1)** |

## 📚 Version History
- 1.0
  - Initial release

## © License

## ❤️ Acknowledgements

