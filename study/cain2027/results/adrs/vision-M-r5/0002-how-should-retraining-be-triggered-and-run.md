# How should retraining be triggered and run?

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained every week from newly labelled images. A small team and limited infrastructure favor a repeatable process with little manual effort.

## Decision Drivers

* Weekly retraining
* Newly labelled images
* Small team

## Considered Options

* Automated retraining pipeline with a weekly schedule (`v:6.5`)
* Manual retraining trigger (`v:6.14`)

## Decision Outcome

Chosen option: "Automated retraining pipeline with a weekly schedule" (`v:6.5`).

Automation suits the small team, and the weekly schedule follows the stated cadence. The design space treats automation and schedule as values of the same low-exclusivity dimension; the point check selected automation as its single value and returned no warnings or attesting sources.

### Consequences

* Build a weekly training and validation workflow.
* Retain a review gate before deployment.

## Pros and Cons of the Options

### Automated retraining pipeline with a weekly schedule

* Good, because Reduces manual effort
* Good, because Fits recurring cadence
* Bad, because Requires pipeline setup
* Bad, because Needs validation safeguards
* Sources: `s06_p07`, `s06_p11`, `s22_p08`

### Manual retraining trigger

* Good, because Human control
* Good, because Low initial automation effort
* Bad, because Recurring operator work
* Bad, because May delay updates
* Sources: `s19_p08`, `s22_p15`
