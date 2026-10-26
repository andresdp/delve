# Promote a validated model version between runs

*How should model ideas reach production?*

* System: Retail demand forecasting

## Context and Problem Statement

The three-person data science team owns the pipeline end to end and wants new model ideas in production quickly without disrupting the weekly run. Model changes need a reviewable path from experiment to production.

## Decision Drivers

* Fast model iteration
* Protect weekly run
* Three-person team

## Considered Options

* Promote a validated model version between runs
* Replace the production model in place

## Decision Outcome

Chosen option: "Promote a validated model version between runs".

Versioned promotion gives the team a short, controlled path to production while keeping the weekly run tied to a known model version.

### Consequences

* Production runs must pin a model version.
* The team must define minimum validation checks and rollback steps.

## Pros and Cons of the Options

### Promote a validated model version between runs

* Good, because Controlled rollout
* Good, because Clear model history
* Bad, because Promotion adds a step
* Bad, because Requires validation criteria

### Replace the production model in place

* Good, because Few deployment steps
* Good, because Fast replacement
* Bad, because Harder rollback
* Bad, because Can disrupt run
