DROP TABLE earthquakes CASCADE;
DROP TABLE alerts CASCADE;
DROP TABLE status CASCADE;
DROP TABLE mag_types CASCADE;
DROP TABLE networks CASCADE;
DROP TABLE types CASCADE;

CREATE TABLE earthquakes (
    earthquake_id VARCHAR UNIQUE NOT NULL,
    magnitude FLOAT NOT NULL,
    lon DECIMAL NOT NULL,
    lat DECIMAL NOT NULL,
    time TIMESTAMP CHECK (time <= CURRENT_TIMESTAMP),
    felt SMALLINT,
    cdi FLOAT,
    mmi REAL,
    alert_id SMALLINT NOT NULL,
    status_id SMALLINT NOT NULL,
    significance SMALLINT NOT NULL,
    network_id SMALLINT NOT NULL,
    nst SMALLINT,
    dmin REAL,
    gap REAL,
    magtype_id SMALLINT NOT NULL,
    type SMALLINT,
    title TEXT NOT NULL,
    depth FLOAT,
    PRIMARY KEY (earthquake_id),
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (status_id) REFERENCES status(status_id),
    FOREIGN KEY (network_id) REFERENCES networks(network_id),
    FOREIGN KEY (type_id) REFERENCES networks(network_id),
    FOREIGN KEY (mag_type_id) REFERENCES mag_types(mag_type_id)
);

CREATE TABLE alerts (
    alert_id UNIQUE SMALLINT GENERATED ALWAYS AS IDENTITY,
    alert_value VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY (alert_id)
);

CREATE TABLE networks (
    network_id UNIQUE SMALLINT GENERATED ALWAYS AS IDENTITY,
    network_name VARCHAR(2) UNIQUE NOT NULL,
    PRIMARY KEY (network_id)
);

CREATE TABLE types (
    type_id UNIQUE SMALLINT GENERATED ALWAYS AS IDENTITY,
    type_value VARCHAR UNIQUE NOT NULL,
    PRIMARY KEY (type_id)
);

CREATE TABLE status (
    status_id UNIQUE SMALLINT GENERATED ALWAYS AS IDENTITY,
    status VARCHAR UNIQUE NOT NULL,
    PRIMARY KEY (status_id)
);

CREATE TABLE mag_types (
    mag_type_id UNIQUE SMALLINT GENERATED ALWAYS AS IDENTITY,
    mag_type_value VARCHAR(3) UNIQUE NOT NULL,
    PRIMARY KEY (mag_type_id)
);

INSERT INTO alerts VALUES ('green'), ('yellow'), ('orange'), ('red');
INSERT INTO networks VALUES ('ak'), ('at'), ('ci'), ('hv'), ('ld'), ('mb'), ('nc'), ('nm'), ('nn'), ('pr'), ('pt'), ('se'), ('us'), ('uu'), ('uw');
INSERT INTO types VALUES ('earthquake'), ('quarry');
INSERT INTO status VALUES ('automatic'), ('reviewed'), ('deleted');
INSERT INTO mag_types VALUES ('md'), ('ml'), ('ms'), ('mw'), ('me'), ('mi'), ('mb'), ('mlg');
