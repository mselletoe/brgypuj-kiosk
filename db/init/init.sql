-- init.sql (runs only the first time)
CREATE TABLE IF NOT EXISTS residents (
    id SERIAL PRIMARY KEY,
    last_name TEXT,
    first_name TEXT,
    middle_name TEXT,
    suffix TEXT,
    sex_gender TEXT,
    age INT,
    birthdate DATE,
    years_residency INT,
    unit_blk_street TEXT,
    brgy TEXT,
    municipality TEXT,
    province TEXT,
    region TEXT
);

-- Import CSV placed beside this file (docker-entrypoint-initdb.d/residents.csv)
COPY residents(last_name, first_name, middle_name, suffix, sex_gender, age, birthdate, years_residency, unit_blk_street, brgy, municipality, province, region)
FROM '/docker-entrypoint-initdb.d/mock_population_amadeo.csv'
DELIMITER ','
CSV HEADER;