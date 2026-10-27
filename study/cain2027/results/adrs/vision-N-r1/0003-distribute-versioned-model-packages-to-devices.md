# Distribute versioned model packages to devices

* System: On-device visual inspection

## Context and Problem Statement

Retrained models must reach cameras along production lines, many of which may be offline. Versioned packages let devices install a known model when connectivity is available.

## Decision Drivers

* Weekly model updates
* Intermittent connectivity
* Small team

## Considered Options

* Versioned model packages
* Stream models on demand

## Decision Outcome

Chosen option: "Versioned model packages".

Packages can be staged and installed when devices regain connectivity, without making inspection depend on a live connection.

### Consequences

* The team must track deployed versions.
* Updates may reach devices at different times.

## Pros and Cons of the Options

### Versioned model packages

* Good, because Repeatable releases
* Good, because Supports deferred installation
* Bad, because Requires package tracking
* Bad, because Devices may lag behind

### Stream models on demand

* Good, because Latest model on request
* Good, because No local package staging
* Bad, because Needs connectivity
* Bad, because Inspection can be blocked
