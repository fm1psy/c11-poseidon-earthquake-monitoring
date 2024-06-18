DROP TABLE earthquakes CASCADE;
DROP TABLE alerts CASCADE;
DROP TABLE status CASCADE;
DROP TABLE mag_types CASCADE;
DROP TABLE networks CASCADE;
DROP TABLE types CASCADE;

CREATE TABLE earthquakes (
    earthquake_id VARCHAR UNIQUE NOT NULL,
    magnitude FLOAT,
    lon DECIMAL NOT NULL,
    lat DECIMAL NOT NULL,
    time TIMESTAMP,
    felt SMALLINT,
    cdi FLOAT,
    mmi REAL,
    alert_id SMALLINT NOT NULL,
    status_id SMALLINT NOT NULL,
    significance SMALLINT NOT NULL,
    network_id SMALLINT NOT NULL,
    nst SMALLINT,
    dmin FLOAT,
    gap FLOAT,
    magtype_id SMALLINT NOT NULL,
    type SMALLINT,
    title TEXT,
    depth FLOAT,
    PRIMARY KEY (earthquake_id)
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (status_id) REFERENCES status(status_id),
    FOREIGN KEY (network_id) REFERENCES networks(network_id),
    FOREIGN KEY (mag_type_id) REFERENCES mag_types(mag_type_id)
);

CREATE TABLE alerts (
    alert_id UNIQUE SMALLINT NOT NULL,
    alert_value VARCHAR(6),
    PRIMARY KEY (alert_id),
);

CREATE TABLE networks (
    network_id UNIQUE SMALLINT NOT NULL,
    network_name VARCHAR(2),
    PRIMARY KEY (network_id)
);

CREATE TABLE types (
    type_id UNIQUE SMALLINT NOT NULL,
    type_value VARCHAR,
    PRIMARY KEY (type_id)
);

CREATE TABLE status (
    status_id UNIQUE SMALLINT NOT NULL,
    status VARCHAR,
    PRIMARY KEY (status_id)
);

CREATE TABLE mag_types (
    mag_type_id UNIQUE SMALLINT NOT NULL,
    mag_type_value VARCHAR(3),
    PRIMARY KEY (mag_type_id)
);



