---
title: Replica trimming for lightly used repositories
type: value
id: '1.7'
status: mixed
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by:
- s01_p08
- s03_p09
rejected_by:
- s01_p08
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p003|P003]]'
tags:
- value
- mixed
- repository-replica-placement
---

# Replica trimming for lightly used repositories

Reduce replica counts for low-demand repositories to avoid fixed redundancy cost.

## Evidence

- **s01_p08** (both) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > This is essentially how Spokes works, and it has been working quite well for the past 13 years. Of course, Spokes is not perfect — no system is. In 2026, the way people use Git repositories has changed drastically, and we have learned many important lessons about building distributed systems along the way. Time and experience have shown which of …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …

## In design points

[[designs/p003|P003]]
