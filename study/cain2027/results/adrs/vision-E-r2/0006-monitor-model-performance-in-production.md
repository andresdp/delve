# Monitor model performance in production

* System: On-device visual inspection

## Context and Problem Statement

The system receives new labels regularly, creating a way to assess deployed model quality and detect regressions.

## Decision Drivers

* Defect quality
* Weekly labels
* Device operation

## Considered Options

* Model performance monitoring (`v:22.1`)
* No in-production monitoring (`v:22.3`)

## Decision Outcome

Chosen option: "Model performance monitoring" (`v:22.1`).

Performance monitoring helps use newly labelled images to identify model regressions and inform subsequent training (d:22, v:22.1).

### Consequences

* Define measurable quality indicators.
* Plan collection or return of labels and outcomes.

## Pros and Cons of the Options

### Model performance monitoring

* Good, because Tracks model quality
* Good, because Supports release decisions
* Bad, because Needs performance measures
* Bad, because Labels may arrive later
* Sources: `d:22`, `v:22.1`

### No in-production monitoring

* Good, because No monitoring overhead
* Bad, because Regressions may go unseen
* Bad, because Weak feedback loop
* Sources: `d:22`, `v:22.3`
