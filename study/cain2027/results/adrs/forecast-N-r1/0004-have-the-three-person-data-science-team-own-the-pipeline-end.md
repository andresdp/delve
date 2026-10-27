# Have the three-person data science team own the pipeline end to end

* System: Retail demand forecasting

## Context and Problem Statement

The brief explicitly assigns end-to-end pipeline ownership to a team of three data scientists.

## Decision Drivers

* Team of three
* End-to-end ownership

## Considered Options

* Data science team owns the pipeline end to end
* Split ownership across specialist teams

## Decision Outcome

Chosen option: "Data science team owns the pipeline end to end".

This follows the stated ownership model; automation and simple operations are important given the team size.

### Consequences

* Operational procedures should suit a small team.
* Support and on-call expectations remain to be decided.

## Pros and Cons of the Options

### Data science team owns the pipeline end to end

* Good, because Matches stated ownership
* Good, because Keeps pipeline knowledge close
* Bad, because Concentrates operational load
* Bad, because Requires maintainable automation

### Split ownership across specialist teams

* Good, because Shares operational duties
* Good, because Allows specialist support
* Bad, because Adds coordination overhead
* Bad, because Ownership is unspecified
