---
type: Design Alternative
title: Commit-triggered staged release automation
description: Repository changes trigger automated builds, tests, artifact promotion, and deployment across delivery stages.
id: '19.2'
dimension: /concepts/ml-release-automation.md
accepted_by:
- s06_p02
- s06_p06
- s06_p13
- s06_p14
- s06_p15
- s08_p01
- s08_p02
- s13_p09
rejected_by: []
passages: 8
includes:
- Unified CI/CD release process
- Commit-triggered CI/CD
- Environment-gated deployment automation
tags:
- value
- accepted
- ml-release-automation
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Commit-triggered staged release automation

Repository changes trigger automated builds, tests, artifact promotion, and deployment across delivery stages.

## Evidence

- **s06_p02** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p06** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p13** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p14** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s06_p15** (accepts) · [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- **s08_p01** (accepts) · [Continuous Intelligence: Moving Machine Learning Application into Production Reliably](/sources/s8.md)
- **s08_p02** (accepts) · [Continuous Intelligence: Moving Machine Learning Application into Production Reliably](/sources/s8.md)
- **s13_p09** (accepts) · [Architectural thinking in the Wild West of data science](/sources/s13.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Unified CI/CD release process**: Models and their surrounding services are treated as software assets and released through one automated process.
- **Commit-triggered CI/CD**: Builds, tests, packages, and promotes pipeline artifacts in response to repository changes.
- **Environment-gated deployment automation**: Uses differing automation and approval levels across test, pre-production, and production environments.
