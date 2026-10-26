# How should consuming teams access classifications?

* System: Large-scale document classification

## Context and Problem Statement

Several teams consume the classifier’s results, so the system needs a shared integration boundary. The brief does not specify synchronous access or latency targets.

## Decision Drivers

* Multiple consuming teams
* Millions of documents daily

## Considered Options

* REST prediction microservice (`v:29.1`)
* PMML-based model serving (`v:29.2`)

## Decision Outcome

Chosen option: "REST prediction microservice" (`v:29.1`).

A shared REST interface suits several independently consuming teams; “How to power up your product by machine learning with python microservice” and “Architecting a Machine Learning Pipeline” describe API-backed prediction services. This adds service operations overhead compared with distributing a model representation.

### Consequences

* Define and version a stable request and response contract.
* The brief does not specify whether consumers call synchronously or read batch results.

## Pros and Cons of the Options

### REST prediction microservice

* Good, because Teams: shared API boundary for integrations
* Good, because Volume: separates classifier service from consumers
* Bad, because Operations: adds a service to maintain
* Sources: `s01_p05`, `s01_p08`, `s02_p10`, `s02_p11`, `s02_p12`, `s03_p01`, `s07_p01`, `s08_p02`, `s09_p03`, `s09_p09`, `s09_p10`, `s10_p03`, `s10_p04`, `s11_p07`, `s16_p03`, `s16_p04`, `s19_p08`, `s19_p14`, `s19_p17`, `s21_p07`, `s23_p07`, `s24_p05`

### PMML-based model serving

* Good, because Portability: shared model representation
* Good, because Volume: supports batch scoring
* Bad, because Teams: requires compatible PMML tooling
