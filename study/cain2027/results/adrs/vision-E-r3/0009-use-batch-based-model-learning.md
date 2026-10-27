# Use batch-based model learning

* System: On-device visual inspection

## Context and Problem Statement

New labels are collected for weekly retraining, and inference must continue on devices without network access. The brief does not call for online updates.

## Decision Drivers

* Weekly retraining
* Offline inference

## Considered Options

* Batch-based learning (`v:19.1`)
* Incremental learning (`v:19.2`)

## Decision Outcome

Chosen option: "Batch-based learning" (`v:19.1`).

Batch learning aligns with weekly labelled data and avoids requiring continuous connectivity or online model updates (d:19, v:19.1).

### Consequences

* Model improvements wait for the next training and delivery cycle.
* Training must validate each candidate before device release.

## Pros and Cons of the Options

### Batch-based learning

* Good, because Matches weekly cadence
* Good, because Training can run offline
* Bad, because Improvements arrive between runs
* Sources: `d:19`, `v:19.1`

### Incremental learning

* Good, because Can incorporate updates continuously
* Bad, because More complex update behavior
* Sources: `d:19`, `v:19.2`
