# Progressive release automation with rollback

*How should weekly model releases be deployed?*

* System: On-device visual inspection

## Context and Problem Statement

Newly retrained models must reach production devices regularly, and a faulty update could disrupt defect detection. The release approach needs to support safe deployment and recovery.

## Decision Drivers

* Reliable inspection
* Weekly updates
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Reliable inspection decides the choice: progressive deployment limits exposure and supports reversion after a bad update. This adds rollout and rollback stages to each weekly release.

### Consequences

* Keep a prior model version available for recovery.
* Automate staged deployment and reversion where feasible.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Reliable inspection: incremental rollout limits exposure
* Good, because Small team: automates deployment and rollback
* Bad, because Weekly updates: rollout adds stages
* Bad, because Small team: rollback process needs maintenance
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`

### Unified release automation

* Good, because Small team: one automated build and release process
* Good, because Weekly updates: streamlines packaging
* Bad, because Reliable inspection: no explicit incremental rollout or rollback
* Bad, because Small team: recovery may require manual work
* Sources: `s02_p11`, `s19_p05`, `s20_p02`, `s20_p05`, `s20_p10`, `s20_p12`
