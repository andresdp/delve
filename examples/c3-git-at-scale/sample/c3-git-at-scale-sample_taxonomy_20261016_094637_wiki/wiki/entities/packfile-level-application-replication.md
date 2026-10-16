---
title: Packfile-level application replication
type: value
id: '22.4'
status: accepted
dimension: '[[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]]'
accepted_by:
- s01_p06
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p004|P004]]'
- '[[designs/p007|P007]]'
tags:
- value
- accepted
- replica-synchronization-mechanism
---

# Packfile-level application replication

Git data is replicated at the packfile and reference-transaction layer without distributing the Git implementation itself.

## Evidence

- **s01_p06** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …

## In design points

[[designs/p004|P004]], [[designs/p007|P007]]
