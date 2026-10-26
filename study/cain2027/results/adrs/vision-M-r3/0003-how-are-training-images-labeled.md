# How are training images labeled?

* System: On-device visual inspection

## Context and Problem Statement

The brief says images are newly labeled each week but does not specify who selects or labels them. The choice affects the quality and effort of each retraining cycle.

## Decision Drivers

* New labeled images
* Small team

## Considered Options

* Human-in-the-loop data labeling (`v:23.1`)
* Active-learning sample selection (`v:23.2`)

## Decision Outcome

Chosen option: "Human-in-the-loop data labeling" (`v:23.1`).

Use human review as the grounded default because the brief establishes labeling but gives no mechanism for sample selection. “Architecture of a real-world Machine Learning system” and “MLOps Principles” describe human-in-the-loop labeling; active learning remains a possible extension.

### Consequences

* Allocate time for review and label quality checks.
* The design space does not determine the labeling workflow details.

## Pros and Cons of the Options

### Human-in-the-loop data labeling

* Good, because Human review supplies labels
* Good, because Fits controlled review
* Bad, because Requires reviewer time
* Bad, because Can slow data preparation
* Sources: `s09_p03`, `s10_p08`, `s22_p17`

### Active-learning sample selection

* Good, because Focuses review on selected samples
* Good, because Can reduce labeling volume
* Bad, because Requires selection logic
* Bad, because Still needs human labels
* Sources: `s24_p08`, `s24_p09`
