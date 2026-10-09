---
title: Poor clone performance
type: value
id: '4.36'
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

# Poor clone performance

Unacceptably slow cloning caused by distributed object storage and packfile transfer constraints.

## Evidence

- **s01_p03** (supports) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
