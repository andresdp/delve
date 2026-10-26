# Promote model changes through staged automation

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly, but must not break the weekly run. Automated builds and tests with staged promotion provide a release path that checks changes before production.

## Decision Drivers

* Fast model iteration
* Weekly run stability

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Weekly run stability decides the choice: staged promotion allows automated delivery while retaining checks before production. “MLOps: Continuous delivery and automation pipelines in machine learning” supports commit-triggered builds and staged release; the trade-off is that gates can slow an individual change.

### Consequences

* Changes pass automated build and test stages before production.
* Promotion depends on passing release gates.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Fast model iteration: repository changes trigger delivery stages
* Bad, because Weekly run stability: failed gates can delay promotion
* Sources: `s06_p02`, `s06_p06`, `s06_p13`, `s06_p14`, `s06_p15`, `s08_p01`, `s08_p02`, `s13_p09`

### Unified release automation

* Good, because Fast model iteration: automates build, test, package, and release
* Bad, because Weekly run stability: less explicit stage-by-stage promotion
* Sources: `s02_p11`, `s19_p05`, `s20_p02`, `s20_p05`, `s20_p10`, `s20_p12`
