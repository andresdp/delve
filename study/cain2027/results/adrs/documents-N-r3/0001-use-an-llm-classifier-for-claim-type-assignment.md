# Use an LLM classifier for claim-type assignment

* System: Large-scale document classification

## Context and Problem Statement

The system classifies incoming documents into claim types, and the brief specifies an LLM-based classifier.

## Decision Drivers

* Claim-type classification
* LLM-based approach

## Considered Options

* LLM classifier
* Rules-based classifier

## Decision Outcome

Chosen option: "LLM classifier".

It directly meets the stated requirement to classify documents with an LLM.

### Consequences

* Requires model evaluation and updates
* Inference capacity affects operating cost

## Pros and Cons of the Options

### LLM classifier

* Good, because Matches brief
* Good, because Flexible classification
* Bad, because Quality needs monitoring
* Bad, because Inference cost

### Rules-based classifier

* Good, because Predictable behavior
* Good, because No model inference
* Bad, because Brittle for varied documents
* Bad, because Rules need maintenance
