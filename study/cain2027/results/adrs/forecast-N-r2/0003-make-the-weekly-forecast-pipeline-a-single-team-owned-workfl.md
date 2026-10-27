# Make the weekly forecast pipeline a single team-owned workflow

* System: Retail demand forecasting

## Context and Problem Statement

The team of three data scientists owns the pipeline end to end, and forecasts are produced weekly. The brief favors a manageable operational shape but does not specify a platform.

## Decision Drivers

* Three-person team
* End-to-end ownership
* Weekly cadence

## Considered Options

* Use one scheduled workflow for data, training, and forecasts
* Split work across independently operated services

## Decision Outcome

Chosen option: "Use one scheduled workflow for data, training, and forecasts".

A single workflow keeps ownership and run status clear for a small team. It can be decomposed later if scale or operational needs justify the added service boundaries.

### Consequences

* The workflow needs clear stages and failure reporting.
* One team remains responsible for the full run.

## Pros and Cons of the Options

### Use one scheduled workflow for data, training, and forecasts

* Good, because One operational view
* Good, because Fewer handoffs
* Bad, because Workflow can grow complex
* Bad, because Failure affects full run

### Split work across independently operated services

* Good, because Independent components
* Good, because Separate scaling
* Bad, because More operational overhead
* Bad, because More integration points
