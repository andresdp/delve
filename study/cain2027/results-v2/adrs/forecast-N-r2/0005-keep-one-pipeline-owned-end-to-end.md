# Keep one pipeline owned end to end

* System: Retail demand forecasting

## Context and Problem Statement

Three data scientists own the pipeline end to end. The brief gives no evidence that separate services or teams are needed for forecasting stages.

## Decision Drivers

* Operational simplicity
* Weekly run reliability
* Fast model iteration

## Considered Options

* Single owned pipeline
* Split into independently operated services

## Decision Outcome

Chosen option: "Single owned pipeline".

Operational simplicity for the three-person team decides the choice; independent stage releases and scaling are sacrificed.

### Consequences

* The team coordinates pipeline releases.
* Stage boundaries can remain modular within the pipeline.

## Pros and Cons of the Options

### Single owned pipeline

* Good, because Operational simplicity: few components
* Good, because Weekly run reliability: coordinated run
* Bad, because Fast model iteration: shared pipeline changes need coordination

### Split into independently operated services

* Good, because Fast model iteration: stages can change separately
* Bad, because Operational simplicity: more interfaces and deployments
* Bad, because Weekly run reliability: more failure points
