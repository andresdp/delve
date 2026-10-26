# How should past forecasts be reproduced?

* System: Retail demand forecasting

## Context and Problem Statement

The brief requires forecasts to be reproducible for any past week. Reproduction depends on retaining the inputs and implementation used for each run.

## Decision Drivers

* Past-week reproducibility
* Weekly runs

## Considered Options

* Versioned inputs, code, and run metadata
* Latest data and code only

## Decision Outcome

Chosen option: "Versioned inputs, code, and run metadata".

Recording the input snapshot, code version, configuration, and model version for each run provides the information needed to reproduce a past week's forecasts.

### Consequences

* Run artifacts and metadata must be retained.
* Pipeline changes must record versions consistently.

## Pros and Cons of the Options

### Versioned inputs, code, and run metadata

* Good, because Traceable run lineage
* Good, because Supports reruns
* Bad, because Storage and retention costs
* Bad, because Requires version discipline

### Latest data and code only

* Good, because Less storage
* Good, because Simple operations
* Bad, because Past runs may change
* Bad, because Weak audit trail
