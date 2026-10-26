# What should automated delivery build, test, and deploy?

* System: On-device visual inspection

## Context and Problem Statement

The system delivers retrained models to production devices. The design space distinguishes deploying served models and system components from deploying pipeline components.

## Decision Drivers

* weekly model delivery
* device deployment
* small team

## Considered Options

* Build, test, and deploy models to be served and other system components (`v:25.1`)
* Build, test, and deploy machine learning pipelines and components needed during pipeline runs (`v:25.2`)

## Decision Outcome

Chosen option: "Build, test, and deploy models to be served and other system components" (`v:25.1`).

The stated delivery need is the retrained model and components used by the inspection application. The checked combination had no warnings, but no attesting sources.

### Consequences

* Include model artifacts in the delivery workflow.
* Coordinate deployment with device availability.

## Pros and Cons of the Options

### Build, test, and deploy models to be served and other system components

* Good, because covers served model delivery
* Bad, because requires device delivery integration
* Sources: `d:25`, `v:25.1`

### Build, test, and deploy machine learning pipelines and components needed during pipeline runs

* Good, because covers pipeline runtime components
* Bad, because does not itself deliver served models
* Sources: `d:25`, `v:25.2`
