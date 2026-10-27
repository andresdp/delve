# Retrain on the weekly schedule

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies a weekly retraining cadence using newly labeled images. The system needs a trigger that reliably starts that cycle.

## Decision Drivers

* Weekly cadence
* New labeled images
* Small team

## Considered Options

* Schedule-based retraining trigger (`v:6.6`)
* Performance- or drift-based retraining trigger (`v:6.8`)

## Decision Outcome

Chosen option: "Schedule-based retraining trigger" (`v:6.6`).

The brief explicitly calls for weekly retraining, so a recurring schedule directly fits the cadence and keeps the trigger understandable for a small team. “MLOps Principles” describes schedule-based retraining (s22_p08).

### Consequences

* Run retraining weekly when labeled data is available.
* A missing-data policy still needs definition.
* The point check returned no warnings, but no adopting sources.

## Pros and Cons of the Options

### Schedule-based retraining trigger

* Good, because Matches weekly cadence
* Good, because Predictable workload
* Bad, because May train without enough data
* Bad, because May miss changes between runs
* Sources: `s02_p08`, `s06_p07`, `s06_p11`, `s20_p06`, `s20_p12`, `s22_p08`, `s24_p07`

### Performance- or drift-based retraining trigger

* Good, because Responds to detected changes
* Good, because Can avoid unnecessary runs
* Bad, because Needs monitoring signals
* Bad, because May not match weekly cadence
* Sources: `s04_p01`, `s04_p12`, `s06_p02`, `s06_p08`, `s06_p11`, `s19_p13`, `s20_p03`, `s20_p05`, `s20_p06`, `s20_p12`, `s21_p09`, `s21_p10`, `s22_p08`, `s22_p15`, `s23_p03`
