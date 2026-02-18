CREATE VIEW gold.daily_encounter_summary AS
SELECT
    CAST(admit_time AS DATE) AS encounter_date,
    scenario,
    acuity,
    COUNT(*) AS encounter_count,
    AVG(los_hours) AS avg_los_hours,
    MIN(los_hours) AS min_los_hours,
    MAX(los_hours) AS max_los_hours
FROM curated.fact_encounters
WHERE admit_time IS NOT NULL
GROUP BY
    CAST(admit_time AS DATE),
    scenario,
    acuity;
