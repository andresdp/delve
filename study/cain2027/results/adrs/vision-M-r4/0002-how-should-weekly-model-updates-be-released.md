# How should weekly model updates be released?

* System: On-device visual inspection

## Context and Problem Statement

Newly labelled images produce a retrained model every week, which must reach devices running offline. A failed update should not leave a line without a usable model.

## Decision Drivers

* Weekly retraining
* Offline devices
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive rollout with rollback limits the impact of a bad weekly model and provides a recovery path for deployed devices. The checked combination with on-device inference and automated hyperparameter optimization was novel and had no warnings; the alternative staged-release point was also novel.

### Consequences

* Keep a known-good model on each device.
* Track rollout and model versions.
* Allow devices to receive updates when connected.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Previous version recovery
* Bad, because Release machinery to maintain
* Bad, because Device rollout coordination
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Commit-triggered staged release automation

* Good, because Automates build and promotion
* Good, because Stage-specific checks
* Bad, because Needs connected release path
* Bad, because May not roll out gradually
* Sources: `s06_p07`, `s06_p11`, `s20_p06`, `s20_p12`, `s22_p08`, `s24_p07`
