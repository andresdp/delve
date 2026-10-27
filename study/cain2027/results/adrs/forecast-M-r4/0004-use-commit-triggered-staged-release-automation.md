# Use commit-triggered staged release automation

* System: Retail demand forecasting

## Context and Problem Statement

The team wants model ideas to reach production quickly while protecting the weekly run from unsafe changes. Repository-triggered validation and staged promotion make each change repeatable.

## Decision Drivers

* Fast model iteration
* Protect weekly run

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Progressive release automation with rollback (`v:19.5`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Commit-triggered builds, tests, and staged promotion support quick iteration with repeatable safeguards. “MLOps: Continuous delivery and automation pipelines in machine learning” describes this release pattern (s06_p02, s06_p13).

### Consequences

* Changes must pass automated validation before promotion.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automates build and tests
* Good, because Promotes through stages
* Bad, because Requires maintained release checks
* Sources: `s06_p02`, `s06_p06`, `s06_p13`, `s06_p14`, `s06_p15`, `s08_p01`, `s08_p02`, `s13_p09`

### Progressive release automation with rollback

* Good, because Incremental production updates
* Good, because Supports rollback
* Bad, because Adds rollout coordination
* Sources: `s04_p02`, `s04_p03`, `s04_p10`, `s04_p12`, `s04_p18`, `s25_p01`, `s25_p06`, `s25_p09`
