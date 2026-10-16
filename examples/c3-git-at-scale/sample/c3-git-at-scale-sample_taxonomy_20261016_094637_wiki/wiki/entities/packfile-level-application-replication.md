---
type: Design Alternative
title: Packfile-level application replication
description: Git data is replicated at the packfile and reference-transaction layer without distributing the Git implementation itself.
id: '22.4'
dimension: /concepts/replica-synchronization-mechanism.md
accepted_by:
- s01_p06
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
design_points:
- /designs/p004.md
- /designs/p007.md
tags:
- value
- accepted
- replica-synchronization-mechanism
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Packfile-level application replication

Git data is replicated at the packfile and reference-transaction layer without distributing the Git implementation itself.

## Evidence

- **s01_p06** (accepts) · [Git at any scale](/sources/s1.md) · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …

## In design points

[P004](/designs/p004.md), [P007](/designs/p007.md)
