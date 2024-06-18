# c11-poseidon-earthquake-monitoring
This project will monitor the United States Geological Survey (USGS) earthquake data feeds, continually extracting and storing data. This data will be used to provide interactive dashboards  and subscribe-able alerts, so that users can make appropriate preparations/decisions with full knowledge of earthquake risks.

# Entity-Relationship Diagram
<img src="./ERD.png" alt="ERD" width="800"/>

The provided Entity-Relationship Diagram (ERD) illustrates a database schema designed for tracking earthquake data. The schema follows the principles of Third Normal Form (3NF). There is a main earthquake table that captures data specific to each earthquake event. Additionally, lookup tables are included for categories such as status, alerts, networks, types, and magtypes.