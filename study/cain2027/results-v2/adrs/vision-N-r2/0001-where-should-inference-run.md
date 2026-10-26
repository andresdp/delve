# Where should inference run?

* System: On-device visual inspection

## Context and Problem Statement

Cameras inspect production lines that often have no network access. The brief gives no latency target, but inspection must remain possible during disconnection.

## Decision Drivers

* Offline operation
* Tight infrastructure budget
* Small team

## Considered Options

* Run inference on each device
* Central inference service

## Decision Outcome

Chosen option: "Run inference on each device".

Offline operation decides the choice; local inference avoids dependence on connectivity. This gives up centralized runtime management and requires device-compatible models.

### Consequences

* Models must fit device compute and storage limits.
* Devices need a supported local inference runtime.

## Pros and Cons of the Options

### Run inference on each device

* Good, because Offline operation: works without network
* Good, because Tight infrastructure budget: avoids inference servers
* Bad, because Small team: device runtime support to maintain

### Central inference service

* Good, because Small team: centralized runtime management
* Bad, because Offline operation: unavailable during disconnection
* Bad, because Tight infrastructure budget: server and network costs
