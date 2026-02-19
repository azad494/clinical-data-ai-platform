# Vitals Generation Rules (Phase 2B)

Design rules for generating clinically believable vitals that are explicitly linked to `encounters` (and therefore `patients`).

## A) Frequency Per Encounter

- Generate one vitals event every `60 minutes` for each encounter.
- Frequency is fixed for all scenarios in Phase 2B.

## B) Time Window Rule

- `event_time` must satisfy:
  - `admit_time <= event_time <= discharge_time`
- Include an event exactly at `admit_time`: `yes`.
- Do not generate events after `discharge_time`.

## C) Scenario To Range Mapping

Ranges below are target generation bands by `scenario`.

| scenario | heart_rate (bpm) | temperature_c (C) | spo2 (%) | systolic_bp (mmHg) | diastolic_bp (mmHg) |
|---|---:|---:|---:|---:|---:|
| routine | 60-100 | 36.3-37.5 | 95-100 | 105-130 | 65-85 |
| chest_pain | 75-115 | 36.0-37.8 | 92-98 | 130-170 | 80-100 |
| sepsis | 95-140 | 38.0-40.2 | 88-95 | 80-105 | 45-70 |
| copd_hypoxia | 80-120 | 36.4-38.0 | 82-92 | 110-150 | 65-95 |

## D) Trend Behavior (Simple)

- `routine`: stable with small noise around baseline values.
- `chest_pain`: mildly elevated vitals with small noise, no major trend shift.
- `sepsis`: worsening for first half of encounter, then improving for second half.
- `copd_hypoxia`: persistently low `spo2` with small fluctuations; other vitals mostly stable with noise.

## Linkage Notes

- Every vitals row must include `encounter_id`, `patient_id`, and `event_time`.
- `patient_id` on vitals must match the patient on the referenced `encounter_id`.
