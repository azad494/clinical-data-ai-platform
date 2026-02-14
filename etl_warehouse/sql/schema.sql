CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS curated;

CREATE TABLE IF NOT EXISTS raw.patients (
    patient_id BIGINT,
    age BIGINT,
    sex VARCHAR
);

CREATE TABLE IF NOT EXISTS raw.encounters (
    encounter_id BIGINT,
    patient_id BIGINT,
    admit_time TIMESTAMP,
    discharge_time TIMESTAMP,
    scenario VARCHAR,
    acuity VARCHAR,
    los_hours DOUBLE
);

CREATE TABLE IF NOT EXISTS curated.dim_patients (
    patient_id BIGINT,
    age BIGINT,
    sex VARCHAR
);

CREATE TABLE IF NOT EXISTS curated.fact_encounters (
    encounter_id BIGINT,
    patient_id BIGINT,
    admit_time TIMESTAMP,
    discharge_time TIMESTAMP,
    scenario VARCHAR,
    acuity VARCHAR,
    los_hours DOUBLE
);
