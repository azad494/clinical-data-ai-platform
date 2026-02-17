CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS curated;
CREATE SCHEMA IF NOT EXISTS gold;

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

CREATE OR REPLACE VIEW gold.daily_encounter_summary AS
WITH base AS (
    SELECT
        CAST(admit_time AS DATE) AS encounter_date,
        scenario,
        acuity,
        los_hours
    FROM curated.fact_encounters
    WHERE admit_time IS NOT NULL
),
daily AS (
    SELECT
        encounter_date,
        COUNT(*) AS total_encounters,
        AVG(los_hours) AS avg_los_hours
    FROM base
    GROUP BY encounter_date
),
mix AS (
    SELECT
        encounter_date,
        scenario,
        acuity,
        COUNT(*) AS encounter_count
    FROM base
    GROUP BY encounter_date, scenario, acuity
)
SELECT
    m.encounter_date,
    m.scenario,
    m.acuity,
    m.encounter_count,
    d.total_encounters,
    d.avg_los_hours
FROM mix m
JOIN daily d
    ON m.encounter_date = d.encounter_date;
