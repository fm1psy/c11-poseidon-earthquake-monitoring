# 🔎 Database
This folder is responsible for creating a database. It includes a SQL script which creates the tables for a PostgreSQL database based off the ERD laid our in the main README file. 
## 📁 Files
| File Name | Description |
| ----------| ----------- |
| **connect.sh** | A bash script which will allow you to connect to the database to make queries. |
| **run_schema.sh** | A bash script which runs the schema.sql file in the database. Since the schema has been set up to be idempotent, this script can be run many times. However, any data in the database will be deleted upon running this script. |
| **schema.sql** | Contains the SQL queries to insert tables into the database. Also includes initial seeding of certain values.|
| **\*.tf** | Files ending in '.tf' are used to terraform the PostgreSQL AWS RDS service used to host our database on the cloud. |


## ❗️❗️ Important
To run the bash scripts, ensure that you have already setup the following environmental variables in a `.env` file:
| Variable Name | Value |
| ------------- | ----- |
| DB_HOST | The public URL of the database. |
| DB_NAME | The name of the database. |
| DB_USERNAME | The username that you will be using to interact with the database. |
| DB_PASSWORD | The password required to interact with the database. |
| DB_PORT | The port the database is listening to. |
| ACCESS_KEY | The unique identifier associated with your AWS account or IAM user.  |
| SECRET_ACCESS_KEY | The 'password' to access your AWS account or IAM user account |


### 🏃‍♂️‍➡️ Running the scripts
All the scripts only require basic commands to be executed. Different commands are used depending on the software. Ensure that you are in the dashboard directory before using these commands.
```
# Terraform
terraform init
terraform apply
yes

# Bash
sh <bash_script.sh>
```