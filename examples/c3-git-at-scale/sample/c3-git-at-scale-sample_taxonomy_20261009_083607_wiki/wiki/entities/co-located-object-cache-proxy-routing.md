---
title: Co-located object-cache proxy routing
type: value
id: '3.26'
status: accepted
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by:
- s05_p08
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
design_points:
- '[[designs/p009|P009]]'
- '[[designs/p023|P023]]'
tags:
- value
- accepted
- replica-failure-repair-and-failover
---

# Co-located object-cache proxy routing

Route large-repository object traffic through caches near users and build machines.

## Evidence

- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[[designs/p009|P009]], [[designs/p023|P023]]
