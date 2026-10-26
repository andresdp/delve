# How should model changes be released?

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas should reach production quickly without breaking the weekly run. A release process can validate and promote changes through stages.

## Decision Drivers

* Fast model iteration
* Weekly run continuity
* Safe promotion

## Considered Options

* Commit-triggered staged release automation (`v:19.2`)
* Unified release automation (`v:19.1`)

## Decision Outcome

Chosen option: "Commit-triggered staged release automation" (`v:19.2`).

Repository-triggered builds and staged promotion support fast iteration while allowing validation before production. Google’s MLOps guidance and Continuous Intelligence describe this release pattern.

### Consequences

* Automated checks must gate promotion.
* Release stages and rollback behavior need configuration.

## Pros and Cons of the Options

### Commit-triggered staged release automation

* Good, because Automates build and promotion
* Good, because Separates release stages
* Bad, because Requires release setup
* Sources: `s06_p02`, `s06_p06`, `s06_p13`, `s06_p14`, `s08_p01`

### Unified release automation

* Good, because One release process
* Good, because Packages model and services
* Bad, because Less explicit stage gating
* Sources: `s02_p11`, `s19_p05`, `s20_p02`
