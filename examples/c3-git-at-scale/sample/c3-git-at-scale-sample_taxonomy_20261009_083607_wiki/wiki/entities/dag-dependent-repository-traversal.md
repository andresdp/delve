---
title: DAG-dependent repository traversal
type: value
id: '4.18'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s01_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
design_points:
- '[[designs/p006|P006]]'
- '[[designs/p014|P014]]'
- '[[designs/p016|P016]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# DAG-dependent repository traversal

Traversing commits, trees, and parents through sequentially dependent Git object lookups.

## Evidence

- **s01_p03** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …

## In design points

[[designs/p006|P006]], [[designs/p014|P014]], [[designs/p016|P016]]
