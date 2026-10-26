# Progressive release automation with rollback

*How should model updates be released?*

* System: On-device visual inspection

## Context and Problem Statement

Trained models must reach devices that may be disconnected, so release needs to tolerate interrupted or problematic updates. The team has limited capacity for manual recovery.

## Decision Drivers

* Device updates
* Offline devices
* Small team

## Considered Options

* Progressive release automation with rollback (`v:19.5`)
* Commit-triggered staged release automation (`v:19.2`)

## Decision Outcome

Chosen option: "Progressive release automation with rollback" (`v:19.5`).

Progressive rollout and rollback limit the impact of a faulty model release while reducing recovery work. “Productionizing Machine Learning with a Microservices Architecture” and the Azure ML deployment guidance support this approach; the checked combination was novel and produced no warnings or attesting sources.

### Consequences

* Keep a known-good model available on devices.
* Account for delayed or interrupted updates.

## Pros and Cons of the Options

### Progressive release automation with rollback

* Good, because Incremental rollout
* Good, because Supports rollback
* Bad, because Requires release coordination
* Bad, because Devices may update at different times
* Sources: `s04_p02`, `s04_p10`, `s25_p01`

### Commit-triggered staged release automation

* Good, because Automates build and promotion
* Good, because Staged validation
* Bad, because Commit-driven cadence
* Bad, because Does not itself ensure device rollback
* Sources: `s25_p06`
