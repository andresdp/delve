# Record the model version and features for each score

* System: Card-fraud scoring service

## Context and Problem Statement

Auditors must later be able to determine which model version and which features produced every score. That requires a durable association between each score and its scoring inputs.

## Decision Drivers

* Auditor traceability
* Tens-of-milliseconds latency

## Considered Options

* Persist score, model version, and feature snapshot asynchronously
* Persist score, model version, and feature snapshot synchronously
* Persist score and model version only

## Decision Outcome

Chosen option: "Persist score, model version, and feature snapshot asynchronously".

Auditor traceability decides the choice: retaining both the model version and feature snapshot supports later inspection. Asynchronous writes protect latency, at the cost of needing to detect and handle missing records.

### Consequences

* Include a stable score identifier with each audit record.
* Monitor delivery failures and record completeness.
* Define retention and access controls for stored feature snapshots.

## Pros and Cons of the Options

### Persist score, model version, and feature snapshot asynchronously

* Good, because Auditor traceability: retains inputs and model identity per score
* Good, because Tens-of-milliseconds latency: keeps durable writes off the response path
* Bad, because Auditor traceability: asynchronous failure can leave gaps

### Persist score, model version, and feature snapshot synchronously

* Good, because Auditor traceability: confirms record persistence before replying
* Bad, because Tens-of-milliseconds latency: storage writes add response time
* Bad, because Peak availability: storage outages can block scoring

### Persist score and model version only

* Good, because Tens-of-milliseconds latency: smaller records to write
* Bad, because Auditor traceability: cannot reconstruct which features produced the score
