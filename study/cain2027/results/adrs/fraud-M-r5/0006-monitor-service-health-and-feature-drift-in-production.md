# Monitor service health and feature drift in production

* System: Card-fraud scoring service

## Context and Problem Statement

Peak availability depends on observing runtime health, and trustworthy scoring depends on detecting changes in inputs and features. Both are relevant to the service after deployment.

## Decision Drivers

* Peak availability
* Feature integrity

## Considered Options

* Service-health and data-quality monitoring (`v:6.23`)
* Passive production operation (`v:6.4`)

## Decision Outcome

Chosen option: "Service-health and data-quality monitoring" (`v:6.23`).

Service and data-quality monitoring addresses availability and input integrity together. “Productionizing Machine Learning with a Microservices Architecture” describes monitoring feature generation and production behavior; passive operation provides no active visibility.

### Consequences

* Monitor latency, uptime, dependencies, and data quality.
* Monitoring signals require ownership and response procedures.

## Pros and Cons of the Options

### Service-health and data-quality monitoring

* Good, because Covers runtime and input health
* Good, because Can reveal feature changes
* Bad, because Needs operational thresholds
* Bad, because Does not itself define audit records
* Sources: `s04_p03`, `s04_p05`, `s04_p12`

### Passive production operation

* Good, because Less monitoring setup
* Good, because Fewer monitoring components
* Bad, because Failures may go unnoticed
* Bad, because Does not support active health checks
* Sources: `s13_p10`, `s21_p07`
