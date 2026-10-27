# Versioned, immutable model packages

*How should model packages be versioned?*

* System: On-device visual inspection

## Context and Problem Statement

Weekly retraining produces successive models that must be pushed across an intermittently connected fleet. Devices and operators need to identify which model is installed.

## Decision Drivers

* weekly releases
* fleet updates
* offline operation

## Considered Options

* Versioned, immutable model packages
* Overwrite a single model artifact

## Decision Outcome

Chosen option: "Versioned, immutable model packages".

Immutable versions make delayed device updates and rollback manageable across weekly releases.

### Consequences

* A registry or equivalent storage must retain package versions.
* Devices need a way to report their installed version.

## Pros and Cons of the Options

### Versioned, immutable model packages

* Good, because traceable releases
* Good, because reproducible deployment
* Bad, because package registry needed
* Bad, because version retention cost

### Overwrite a single model artifact

* Good, because simple storage
* Good, because simple naming
* Bad, because weak traceability
* Bad, because rollback difficulty
