# 🌎 c11-poseidon-earthquake-monitoring

This project will monitor the United States Geological Survey (USGS) earthquake data feeds, continually extracting and storing data. This data will be used to provide interactive dashboards  and subscribable alerts, so that users can make appropriate preparations/decisions with full knowledge of earthquake risks.

## 🗄️ Folders

| Folder Name | Description |
|---|---|
| **api** | An API to allow developers to query earthquake data. |
| **database** | A database to store all the real-time earthquake data. |
| **diagrams**  | Images that map out the project for easy understanding. |
| **.github** | Essential files for your GitHub repository. |
| **pipeline**  | Code that brings data from the QuakeML API to the database. |

## 📐 Architecture Design

For a visual representation of the project architecture and details on the design decisions, please refer to this section.

### ☁️ Cloud Resources
For this project, we have designed it with the intention of hosting everything on the cloud in order to automate it. The python scripts can still be ran locally but the terraform scripts have been included within the repository if you desire to host this system on the cloud as well. The cloud service that has been used is **AWS**.

### 📐 Architecture Diagram

![Architecture Diagram](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/blob/main/diagrams/architecture_diagram.png)

### ✏️ Design Decisions

## 📏 Database Design

For a visual representation of the database schema and details on the design decisions, please refer to this section.

### 🪧 Entity-Relationship Diagram (ERD)

The provided Entity-Relationship Diagram (ERD) illustrates a database schema designed for tracking earthquake data. The schema follows the principles of Third Normal Form (3NF). There is a main earthquake table that captures data specific to each earthquake event. Additionally, lookup tables are included for categories such as status, alerts and networks.

![ERD Diagram](https://github.com/fm1psy/c11-poseidon-earthquake-monitoring/blob/main/diagrams/erd_diagram.png)

### 💡 Design Decisions


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

### 🌱 Database Seeding with .env configuration

1. **Create an `.env` file in `database` folder**

2. **Edit the .env file to provide the following database connection details**

| ✨ KEY | Placeholder |
|---|---|
|  DB_HOST | _localhost_ |
|  DB_PORT  |  _3306_ |
|  DB_PASSWORD  |  *your_username*  |
|  DB_USER  |  *your_password*  |
|  DB_NAME  |  *your_db_name*  |


> [!IMPORTANT]  
> To be able to run these scripts the following details must be provided in the `.env` file and should NOT be shared.

3. **Run these commands (TO BE CONFIRMED)**:
    ```bash
    cd database
    source .env
    psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -W $DB_PASSWORD -f schema.sql
    python3 seeding.py
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

