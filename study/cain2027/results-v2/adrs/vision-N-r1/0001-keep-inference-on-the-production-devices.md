# Keep inference on the production devices

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect products on lines that often have no network access. Defect detection must therefore work without a cloud connection.

## Decision Drivers

* Network independence
* Weekly model updates
* Tight infrastructure budget

## Considered Options

* On-device inference
* Cloud inference

## Decision Outcome

Chosen option: "On-device inference".

Network independence decides the choice: inference must run locally. This gives up centralized runtime management and makes device deployment part of the system.

### Consequences

* Each device needs a compatible inference runtime.
* Model updates must reach devices when connectivity permits.

## Pros and Cons of the Options

### On-device inference

* Good, because Network independence: works offline
* Good, because Tight infrastructure budget: avoids per-inference cloud compute
* Bad, because Weekly model updates: requires device distribution
* Bad, because Small team: device runtime support

### Cloud inference

* Good, because Small team: centralized runtime
* Bad, because Network independence: unavailable offline
* Bad, because Tight infrastructure budget: ongoing compute and transfer costs
