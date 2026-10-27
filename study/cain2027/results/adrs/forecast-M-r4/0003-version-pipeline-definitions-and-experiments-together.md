# Version pipeline definitions and experiments together

* System: Retail demand forecasting

## Context and Problem Statement

The team must reproduce forecasts for any past week and compare new model ideas safely. That requires retaining the pipeline and experiment context alongside model artifacts.

## Decision Drivers

* Past-week reproducibility
* Model comparison

## Considered Options

* Pipeline and experiment version control (`v:20.2`)
* Comprehensive ML lifecycle traceability (`v:20.3`)

## Decision Outcome

Chosen option: "Pipeline and experiment version control" (`v:20.2`).

This option directly covers the pipeline and experiment history needed to compare and reproduce runs, while comprehensive lifecycle traceability adds scope beyond the brief. “Productionizing Machine Learning with a Microservices Architecture” discusses versioning pipeline and ML assets (s04_p01, s04_p15).

### Consequences

* Past runs require retained pipeline and artifact versions.

## Pros and Cons of the Options

### Pipeline and experiment version control

* Good, because Tracks pipeline and results
* Good, because Supports comparison
* Bad, because Adds versioned assets to manage
* Sources: `s04_p01`, `s04_p03`, `s04_p05`, `s04_p15`, `s04_p18`, `s17_p03`

### Comprehensive ML lifecycle traceability

* Good, because Broad lifecycle links
* Good, because Tracks datasets and health
* Bad, because Broader governance scope
* Sources: `s08_p01`, `s08_p02`, `s22_p03`, `s22_p04`, `s22_p06`, `s22_p08`, `s22_p13`, `s22_p17`
