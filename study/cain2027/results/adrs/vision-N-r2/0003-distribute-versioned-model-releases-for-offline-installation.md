# Distribute versioned model releases for offline installation

* System: On-device visual inspection

## Context and Problem Statement

Models are pushed to devices that may not have network access. Releases therefore need to be available for installation when a device can receive them.

## Decision Drivers

* Intermittent connectivity
* Weekly model releases
* Small team

## Considered Options

* Versioned model package with staged device rollout
* Always-on remote model serving

## Decision Outcome

Chosen option: "Versioned model package with staged device rollout".

A package can be transferred when connectivity is available, and staging reduces the risk of pushing a faulty release to every camera.

### Consequences

* Devices may temporarily run different model versions
* Release and installation status need tracking

## Pros and Cons of the Options

### Versioned model package with staged device rollout

* Good, because Supports offline transfer
* Good, because Limits rollout impact
* Bad, because Requires rollout tracking

### Always-on remote model serving

* Good, because Centralized model updates
* Bad, because Requires connectivity
* Bad, because Adds infrastructure cost
