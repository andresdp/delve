---
title: Distributed object-level Git storage
type: value
id: '2.29'
status: rejected
dimension: '[[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]'
accepted_by: []
rejected_by:
- s01_p03
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
tags:
- value
- rejected
- write-coordination-and-replica-consistency
---

# Distributed object-level Git storage

Storing Git objects individually in a distributed key-value store or hash table.

## Evidence

- **s01_p03** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
