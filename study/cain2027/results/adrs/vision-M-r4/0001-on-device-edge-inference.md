# On-device edge inference

*Where should inference run?*

* System: On-device visual inspection

## Context and Problem Statement

Cameras must inspect products while production lines may have no network access. The brief also limits the team and infrastructure budget.

## Decision Drivers

* Offline operation
* Small team
* Tight budget

## Considered Options

* On-device edge inference (`v:30.4`)
* Containerized inference deployment (`v:30.19`)

## Decision Outcome

Chosen option: "On-device edge inference" (`v:30.4`).

On-device inference keeps inspection available during network outages and directly fits the cameras on the production lines. The design point is unattested in the workspace, so this is a brief-driven choice rather than a source-backed combination.

### Consequences

* Deploy model updates to line devices.
* Plan for device resource limits.
* Use local operation when disconnected.

## Pros and Cons of the Options

### On-device edge inference

* Good, because Works without network
* Good, because Local predictions
* Bad, because Device deployment effort
* Bad, because Hardware constraints
* Sources: `s01_p06`, `s07_p01`, `s19_p11`, `s24_p01`, `s25_p07`

### Containerized inference deployment

* Good, because Packages dependencies
* Good, because Portable runtime
* Bad, because Container support needed
* Bad, because Deployment upkeep
* Sources: `s04_p02`, `s06_p07`, `s07_p03`, `s19_p17`
