# Human-in-the-loop data labeling

*How should labeled images be produced?*

* System: On-device visual inspection

## Context and Problem Statement

The brief says each weekly model retraining uses newly labeled images, so label creation is part of the recurring workflow.

## Decision Drivers

* weekly retraining
* labeled images
* small team

## Considered Options

* Human-in-the-loop data labeling (`v:23.1`)
* Active-learning sample selection (`v:23.2`)

## Decision Outcome

Chosen option: "Human-in-the-loop data labeling" (`v:23.1`).

The brief already specifies newly labeled images, and human review provides a grounded way to create them. Active learning could prioritize review, but the brief does not require it.

### Consequences

* Reserve reviewer time each week.
* Maintain a controlled labeling workflow.

## Pros and Cons of the Options

### Human-in-the-loop data labeling

* Good, because domain review
* Good, because controlled labels
* Bad, because review effort
* Bad, because labeling throughput limits
* Sources: `s09_p03`, `s10_p08`, `s22_p17`

### Active-learning sample selection

* Good, because targets uncertain cases
* Good, because reduces review volume
* Bad, because needs selection logic
* Bad, because depends on reviewer capacity
