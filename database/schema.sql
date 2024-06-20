DROP TABLE IF EXISTS earthquakes CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS statuses CASCADE;
DROP TABLE IF EXISTS magtypes CASCADE;
DROP TABLE IF EXISTS networks CASCADE;
DROP TABLE IF EXISTS types CASCADE;

CREATE TABLE alerts (
    alert_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    alert_value VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY (alert_id)
);

CREATE TABLE networks (
    network_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    network_name VARCHAR(2) UNIQUE NOT NULL,
    PRIMARY KEY (network_id)
);

CREATE TABLE types (
    type_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    type_value VARCHAR(20) UNIQUE NOT NULL,
    PRIMARY KEY (type_id)
);

CREATE TABLE statuses (
    status_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    status VARCHAR(9) UNIQUE NOT NULL,
    PRIMARY KEY (status_id)
);

CREATE TABLE magtypes (
    magtype_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    magtype_value VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY (magtype_id)
);

CREATE TABLE earthquakes (
    earthquake_id VARCHAR(20) UNIQUE NOT NULL PRIMARY KEY,
    magnitude REAL NOT NULL,
    lon DECIMAL(9, 6) NOT NULL,
    lat DECIMAL(8, 6) NOT NULL,
    time TIMESTAMP NOT NULL CHECK (time <= CURRENT_TIMESTAMP),
    felt SMALLINT,
    cdi REAL,
    mmi REAL,
    alert_id SMALLINT,
    status_id SMALLINT NOT NULL,
    significance SMALLINT NOT NULL,
    network_id SMALLINT NOT NULL,
    nst SMALLINT,
    dmin REAL,
    gap REAL,
    magtype_id SMALLINT NOT NULL,
    type_id SMALLINT NOT NULL,
    title TEXT NOT NULL,
    depth REAL NOT NULL,
    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (network_id) REFERENCES networks(network_id),
    FOREIGN KEY (type_id) REFERENCES types(type_id),
    FOREIGN KEY (magtype_id) REFERENCES magtypes(magtype_id)
);

INSERT INTO alerts (alert_value) VALUES ('green'), ('yellow'), ('orange'), ('red');
INSERT INTO networks (network_name) VALUES ('ak'), ('at'), ('ci'), ('hv'), ('ld'), ('mb'), ('nc'), ('nm'), ('nn'), ('pr'), ('pt'), ('se'), ('us'), ('uu'), ('uw');
INSERT INTO types (type_value) VALUES ('earthquake'), ('quarry');
INSERT INTO statuses (status) VALUES ('automatic'), ('reviewed'), ('deleted');
INSERT INTO magtypes (magtype_value) VALUES ('md'), ('ml'), ('ms'), ('mw'), ('me'), ('mi'), ('mb'), ('mlg');
