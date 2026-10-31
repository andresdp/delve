# Use batch based serving for document classifications

* System: Large-scale document classification

## Context and Problem Statement

The system classifies millions of documents daily, with seasonal volume changes; the brief gives no real time response requirement. The design space includes scheduled batch serving and real time alternatives (d:5).

## Decision Drivers

* Millions of documents daily
* Seasonal volume changes
* Results used by several teams

## Considered Options

* Data batch based model serving (`v:5.3`)
* Microservice based model serving (`v:5.1`)

## Decision Outcome

Chosen option: "Data batch based model serving" (`v:5.3`).

Batch serving matches the stated high, seasonally varying volume and there is no requirement for immediate results. The checked point had no attesting systems, so this is a novel combination in the design space.

### Consequences

* Teams read completed results from storage.
* Processing cadence and completion delays need agreement.

## Pros and Cons of the Options

### Data batch based model serving

* Good, because Processes on a schedule
* Good, because Writes results to storage
* Bad, because Results arrive after batch processing
* Sources: `d:5`, `v:5.3`

### Microservice based model serving

* Good, because Real time predictions
* Good, because Distributed service
* Bad, because Always on serving path
* Sources: `d:5`, `v:5.1`
