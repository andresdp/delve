# Automated hyperparameter optimization

*How should weekly model candidates be trained and tuned?*

* System: On-device visual inspection

## Context and Problem Statement

Retraining occurs on a weekly cadence, while the infrastructure budget and team size are limited.

## Decision Drivers

* weekly cadence
* small team
* tight budget

## Considered Options

* Automated hyperparameter optimization (`v:28.4`)
* Manual hyperparameter tuning (`v:28.5`)

## Decision Outcome

Chosen option: "Automated hyperparameter optimization" (`v:28.4`).

A bounded automated search can make weekly retraining repeatable for a small team; cap its compute to fit the budget. The checked point produced no warnings but was unattested, so this remains a brief-driven choice rather than a source-attested combination.

### Consequences

* Set a fixed search budget and time limit.
* Compare candidates against a held-out evaluation set.

## Pros and Cons of the Options

### Automated hyperparameter optimization

* Good, because repeatable search
* Good, because less manual tuning
* Bad, because uses training compute
* Bad, because adds workflow complexity

### Manual hyperparameter tuning

* Good, because direct control
* Good, because low setup effort
* Bad, because recurring specialist effort
* Bad, because slower comparisons
* Sources: `s06_p06`, `s17_p03`
