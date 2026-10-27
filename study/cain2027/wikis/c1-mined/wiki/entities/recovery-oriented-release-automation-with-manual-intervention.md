---
type: Design Alternative
title: Recovery-oriented release automation with manual intervention
description: The release process supports automated deployment and restoration of prior versions, while allowing manual debugging or deployment during service recovery.
id: '19.4'
dimension: /concepts/ml-release-automation.md
accepted_by:
- s21_p02
- s21_p03
- s21_p09
- s21_p10
- s21_p11
- s21_p18
- s22_p01
- s22_p03
- s22_p15
rejected_by: []
passages: 9
includes:
- Unified CI/CD release process
- Commit-triggered CI/CD
- Environment-gated deployment automation
- Previous-version rollback
- Manual model debugging and deployment
tags:
- value
- accepted
- ml-release-automation
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Recovery-oriented release automation with manual intervention

The release process supports automated deployment and restoration of prior versions, while allowing manual debugging or deployment during service recovery.

## Evidence

- **s21_p02** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s21_p03** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s21_p09** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s21_p10** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s21_p11** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s21_p18** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s22_p01** (accepts) · [MLOps Principles](/sources/s22.md)
- **s22_p03** (accepts) · [MLOps Principles](/sources/s22.md)
- **s22_p15** (accepts) · [MLOps Principles](/sources/s22.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Unified CI/CD release process**: Models and their surrounding services are treated as software assets and released through one automated process.
- **Commit-triggered CI/CD**: Builds, tests, packages, and promotes pipeline artifacts in response to repository changes.
- **Environment-gated deployment automation**: Uses differing automation and approval levels across test, pre-production, and production environments.
- **Previous-version rollback**: Release operations retain and restore a prior model or software version when a deployment has problems.
- **Manual model debugging and deployment**: Performing model debugging and deployment manually during service restoration.
