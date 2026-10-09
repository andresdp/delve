---
title: Distributed-store traversal round trips
type: value
id: '4.35'
status: outcome
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
tags:
- value
- outcome
- client-repository-workload-scaling
---

# Distributed-store traversal round trips

Repeated remote lookups required by dependent Git DAG traversal.

## Evidence

- **s01_p03** (supports) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
