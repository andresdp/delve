# How should model changes reach production?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, while the weekly forecast run must remain reliable. The team owns the pipeline end to end, so the release path should be straightforward to operate.

## Decision Drivers

* Safe weekly run
* Fast model promotion
* Small-team ownership

## Considered Options

* Validate candidates, then promote explicitly
* Replace the production model in the weekly run
* Run a separate shadow forecast before promotion

## Decision Outcome

Chosen option: "Validate candidates, then promote explicitly".

Protecting the weekly run decides the choice: validate a candidate before switching production to it. This gives up some promotion speed compared with replacing the model directly in the weekly run.

### Consequences

* Keep the current production model active until promotion.
* Define validation checks before release.
* A failed candidate does not block the weekly forecast.

## Pros and Cons of the Options

### Validate candidates, then promote explicitly

* Good, because Safe weekly run: validate before promotion
* Good, because Fast model promotion: focused release step
* Bad, because Small-team ownership: maintain validation and promotion steps

### Replace the production model in the weekly run

* Good, because Small-team ownership: fewer release steps
* Good, because Fast model promotion: immediate use
* Bad, because Safe weekly run: candidate failure can disrupt forecasts

### Run a separate shadow forecast before promotion

* Good, because Safe weekly run: compare without changing production
* Good, because Fast model promotion: evidence from production inputs
* Bad, because Small-team ownership: operate an additional run
* Bad, because Cost: duplicate forecasting work
