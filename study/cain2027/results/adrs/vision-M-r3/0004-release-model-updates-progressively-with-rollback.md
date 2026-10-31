# Release model updates progressively with rollback

* System: On-device visual inspection

## Context and Problem Statement

Retrained models are pushed to production devices. A problematic update could affect defect inspection across the production line.

## Decision Drivers

* Weekly model pushes
* Production-line operation
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive rollout and rollback provide a recovery path when a new model causes problems on production devices. “Productionizing Machine Learning with a Microservices Architecture” describes staged releases and rollback (s04_p02, s04_p03, s04_p10, s04_p12, s04_p18).

### Consequences

* Keep a known-good model available for restoration.
* Define device rollout stages and health checks.
* The combination checked by `ddspace point` was unattested.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Limits rollout exposure
* Good, because Supports version rollback
* Bad, because Requires rollout coordination
* Bad, because Adds release checks
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Unified release automation

* Good, because One automated process
* Good, because Builds and packages together
* Bad, because Less explicit rollout staging
* Bad, because Rollback is not inherent
* Sources: `s02_p11`, `s19_p05`, `s20_p02`, `s20_p05`, `s20_p10`, `s20_p12`
