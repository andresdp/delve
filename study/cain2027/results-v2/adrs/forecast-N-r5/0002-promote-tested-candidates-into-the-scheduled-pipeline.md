# Promote tested candidates into the scheduled pipeline

*How should new model ideas reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

Three data scientists own the pipeline, and the brief calls for rapid model iteration without disrupting the weekly run. Candidate changes need a path to production that keeps them separate from that run until accepted.

## Decision Drivers

* Protect weekly run
* Fast experimentation
* Small team operations

## Considered Options

* Promote tested candidates into the scheduled pipeline
* Edit the production pipeline for each experiment

## Decision Outcome

Chosen option: "Promote tested candidates into the scheduled pipeline".

Protecting the weekly run decides the choice: promote only accepted candidates, at the cost of a deliberate promotion step.

### Consequences

* Candidate evaluation and promotion criteria must be defined.
* The scheduled run uses only a promoted model and pipeline version.

## Pros and Cons of the Options

### Promote tested candidates into the scheduled pipeline

* Good, because Protect weekly run: candidate changes stay separate until accepted
* Good, because Fast experimentation: candidates can be tested independently
* Bad, because Small team operations: needs a promotion step

### Edit the production pipeline for each experiment

* Good, because Fast experimentation: direct path to trying changes
* Bad, because Protect weekly run: experiments can disrupt production
