# Model development process

* System: Retail demand forecasting

## Context and Problem Statement

A team of three data scientists owns the pipeline end to end and wants model ideas to reach production quickly. Short cycles support experimentation, while automated checks and release controls protect the weekly run.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Small team ownership

## Considered Options

* Lean iterative ML development (`v:40.1`)
* Cross-functional ML delivery team (`v:40.7`)

## Decision Outcome

Chosen option: "Lean iterative ML development" (`v:40.1`).

Fast model iteration decides the choice, given the small team and the request to move ideas quickly. The team must pair short cycles with the pipeline validation and rollback controls captured in other decisions.

### Consequences

* Deliver candidate improvements in small increments.
* Keep production promotion behind validation gates.

## Pros and Cons of the Options

### Lean iterative ML development

* Good, because Fast iteration: short development cycles
* Bad, because Protect weekly run: needs release safeguards
* Sources: `s01_p06`, `s06_p06`

### Cross-functional ML delivery team

* Good, because Protect weekly run: combines delivery skills
* Bad, because Small team ownership: requires additional roles
