---
type: Design Alternative
title: Environment-gated deployment automation
description: Deployment automation varies by environment, with progressively stronger validation and approval gates before production.
id: '19.3'
dimension: /concepts/ml-release-automation.md
accepted_by:
- s09_p11
- s10_p07
rejected_by: []
passages: 2
includes:
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

# Environment-gated deployment automation

Deployment automation varies by environment, with progressively stronger validation and approval gates before production.

## Evidence

- **s09_p11** (accepts) · [Architecture of a real-world Machine Learning system](/sources/s9.md)
- **s10_p07** (accepts) · [Architecting a Machine Learning System for Risk](/sources/s10.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Environment-gated deployment automation**: Uses differing automation and approval levels across test, pre-production, and production environments.
