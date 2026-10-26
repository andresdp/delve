# Precompute serving

*How should forecasts be delivered?*

* System: Retail demand forecasting

## Context and Problem Statement

The system produces weekly forecasts, with no stated request for interactive or real-time predictions (d:5).

## Decision Drivers

* Weekly run
* Small team
* Fast iteration

## Considered Options

* Precompute serving (`v:5.4`)
* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Precompute serving" (`v:5.4`).

The weekly run decides the choice: precomputed forecasts match the requested delivery cadence and reduce operational work, giving up immediate availability for model changes.

### Consequences

* Publish a forecast artifact for each weekly run.
* Associate each artifact with its model and data versions.

## Pros and Cons of the Options

### Precompute serving

* Good, because Weekly run: forecasts are ready as reports
* Good, because Small team: avoids a live prediction service
* Bad, because Fast iteration: changes appear at the next forecast run
* Sources: `d:5`, `v:5.4`

### Data batch based model serving

* Good, because Weekly run: writes scheduled predictions to storage
* Bad, because Small team: requires serving-job and storage operations
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Fast iteration: serves predictions as needed
* Bad, because Small team: adds live service operations
* Bad, because Weekly run: real-time capability is not required
* Sources: `d:5`, `v:5.1`
