---
type: Design Alternative
title: Progressive release automation with rollback
description: Production updates are introduced incrementally and can be reverted to a previous version when the release causes problems.
id: '19.5'
dimension: /concepts/ml-release-automation.md
accepted_by:
- s04_p02
- s04_p03
- s04_p10
- s04_p12
- s04_p18
- s25_p01
- s25_p06
- s25_p09
rejected_by: []
passages: 8
includes:
- Unified CI/CD release process
- Commit-triggered CI/CD
- Environment-gated deployment automation
- Previous-version rollback
- Rolling-upgrade release
tags:
- value
- accepted
- ml-release-automation
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Progressive release automation with rollback

Production updates are introduced incrementally and can be reverted to a previous version when the release causes problems.

## Evidence

- **s04_p02** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p03** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p10** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p12** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s04_p18** (accepts) · [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- **s25_p01** (accepts) · [MLOps: Model management, deployment, and monitoring with Azure Machine Learning](/sources/s25.md)
- **s25_p06** (accepts) · [MLOps: Model management, deployment, and monitoring with Azure Machine Learning](/sources/s25.md)
- **s25_p09** (accepts) · [MLOps: Model management, deployment, and monitoring with Azure Machine Learning](/sources/s25.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Unified CI/CD release process**: Models and their surrounding services are treated as software assets and released through one automated process.
- **Commit-triggered CI/CD**: Builds, tests, packages, and promotes pipeline artifacts in response to repository changes.
- **Environment-gated deployment automation**: Uses differing automation and approval levels across test, pre-production, and production environments.
- **Previous-version rollback**: Release operations retain and restore a prior model or software version when a deployment has problems.
- **Rolling-upgrade release**: Updates production systems incrementally without planned downtime.
