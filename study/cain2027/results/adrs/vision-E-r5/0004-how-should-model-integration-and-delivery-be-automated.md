# How should model integration and delivery be automated?

* System: On-device visual inspection

## Context and Problem Statement

A newly retrained model must be pushed to devices, while the team has limited capacity for manual release work.

## Decision Drivers

* Weekly model releases
* Small team
* Device delivery

## Considered Options

* CI/CD pipeline (`v:8.1`)
* Build and Deployment scripts (`v:8.2`)
* No integration or delivery automation (`v:8.4`)

## Decision Outcome

Chosen option: "CI/CD pipeline" (`v:8.1`).

A CI/CD pipeline can automate recurring model delivery; the checked point had no warnings, though the design space attests no sources to this combination.

### Consequences

* Pipeline setup and maintenance add work for the small team.

## Pros and Cons of the Options

### CI/CD pipeline

* Good, because Automates release steps
* Good, because Supports repeatable delivery
* Bad, because Requires pipeline setup
* Sources: `d:8`, `v:8.1`

### Build and Deployment scripts

* Good, because Direct, lightweight automation
* Bad, because More manual coordination
* Sources: `d:8`, `v:8.2`

### No integration or delivery automation

* Good, because No automation setup
* Bad, because Manual release burden
* Sources: `d:8`, `v:8.4`
