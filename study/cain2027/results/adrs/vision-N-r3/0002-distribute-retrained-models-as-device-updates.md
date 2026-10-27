# Distribute retrained models as device updates

* System: On-device visual inspection

## Context and Problem Statement

The model is retrained weekly and must reach production devices, some of which are offline. The brief does not specify a deployment platform or update protocol.

## Decision Drivers

* Weekly retraining
* Intermittent connectivity
* Tight infrastructure budget

## Considered Options

* Device-initiated update polling
* Always-on central push

## Decision Outcome

Chosen option: "Device-initiated update polling".

Polling allows devices to retrieve weekly model updates when they have network access, without requiring a continuously reachable connection.

### Consequences

* Offline devices may run older models until reconnecting.
* The system needs a way to identify the latest approved model.

## Pros and Cons of the Options

### Device-initiated update polling

* Good, because Simple distribution flow
* Good, because Devices choose when connected
* Bad, because Updates may be delayed
* Bad, because Polling requires coordination

### Always-on central push

* Good, because Prompt rollout
* Good, because Central control
* Bad, because Requires connectivity
* Bad, because More infrastructure
