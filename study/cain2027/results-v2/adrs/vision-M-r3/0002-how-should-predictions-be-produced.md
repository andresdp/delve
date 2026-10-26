# How should predictions be produced?

* System: On-device visual inspection

## Context and Problem Statement

Defect checks happen on cameras at production lines where network access may be unavailable. The brief gives no response-time target, but local inference avoids depending on a remote prediction path.

## Decision Drivers

* Offline operation
* Low latency

## Considered Options

* Scheduled batch prediction deployment (`v:31.3`)
* Online computation serving (`v:31.5`)

## Decision Outcome

Chosen option: "Online computation serving".

Offline operation decides where computation happens: use online computation locally on each device, without a remote request. The design space does not specifically ground local online inference, so this choice is an interpretation of the brief rather than an attested alternative.

### Consequences

* Run prediction as images arrive at the camera.
* No numerical latency or throughput target is established.

## Pros and Cons of the Options

### Scheduled batch prediction deployment

* Good, because Low cost: scores on a schedule
* Bad, because Low latency: results are not request-time
* Bad, because Offline operation: device inputs may not reach batch system
* Sources: `s01_p08`, `s02_p02`, `s02_p12`

### Online computation serving

* Good, because Low latency: scores current context immediately
* Bad, because Offline operation: often depends on reachable service
