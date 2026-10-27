---
type: Design Alternative
title: Integrated end-to-end data governance
description: Data governance is implemented as an integrated lifecycle covering traceable ingestion, cataloging, preservation, privacy protection, and policy compliance.
id: '42.5'
dimension: /concepts/ml-data-governance-and-preservation.md
accepted_by:
- s05_p02
- s05_p06
- s19_p02
- s19_p03
rejected_by: []
passages: 4
includes:
- Provenance-preserving data ingestion
- Dataset metadata cataloging
- Immutable original-data preservation
- Privacy-preserving data preparation
- Programmatic data-policy compliance testing
tags:
- value
- accepted
- ml-data-governance-and-preservation
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Integrated end-to-end data governance

Data governance is implemented as an integrated lifecycle covering traceable ingestion, cataloging, preservation, privacy protection, and policy compliance.

## Evidence

- **s05_p02** (accepts) · [Microservices Suck for Machine Learning (and what we did about it)](/sources/s5.md)
- **s05_p06** (accepts) · [Microservices Suck for Machine Learning (and what we did about it)](/sources/s5.md)
- **s19_p02** (accepts) · [Three Levels of ML Software](/sources/s19.md)
- **s19_p03** (accepts) · [Three Levels of ML Software](/sources/s19.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Provenance-preserving data ingestion**: Tracks source origin, metadata, original copies, formats, and privacy handling during ingestion.
- **Dataset metadata cataloging**: Records dataset size, format, aliases, modification time, access controls, profiling, and versions.
- **Immutable original-data preservation**: Works on copies while retaining original datasets for reproducibility and recovery.
- **Privacy-preserving data preparation**: Anonymizes or removes sensitive information to satisfy privacy requirements.
- **Programmatic data-policy compliance testing**: Checks data and feature pipelines automatically against privacy and regulatory policies.
