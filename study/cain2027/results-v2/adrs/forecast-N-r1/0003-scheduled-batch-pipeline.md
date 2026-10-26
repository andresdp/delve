# Scheduled batch pipeline

*How should weekly forecasting be orchestrated?*

* System: Retail demand forecasting

## Context and Problem Statement

Forecasts are produced weekly for each store and product. The three-person team owns the pipeline, so the run needs a clear, repeatable execution path with limited operational overhead.

## Decision Drivers

* Safe weekly run
* Small-team ownership
* Reproducibility: any past week

## Considered Options

* Scheduled batch pipeline
* Manual execution
* Continuously running forecast service

## Decision Outcome

Chosen option: "Scheduled batch pipeline".

A safe weekly run decides the choice: scheduled batch execution matches the forecast cadence and makes run boundaries explicit. It still requires recording inputs and versions to support historical reproduction.

### Consequences

* Schedule and monitor one weekly forecast run.
* Record run status and the versions used.
* Handle failures with an operational recovery procedure.

## Pros and Cons of the Options

### Scheduled batch pipeline

* Good, because Safe weekly run: explicit scheduled execution
* Good, because Small-team ownership: familiar operating model
* Bad, because Reproducibility: must record run inputs and versions

### Manual execution

* Good, because Small-team ownership: minimal orchestration setup
* Bad, because Safe weekly run: dependent on operator actions
* Bad, because Reproducibility: run steps may vary

### Continuously running forecast service

* Good, because Safe weekly run: service can be monitored continuously
* Bad, because Small-team ownership: more infrastructure to operate
* Bad, because Reproducibility: requires explicit historical request handling
