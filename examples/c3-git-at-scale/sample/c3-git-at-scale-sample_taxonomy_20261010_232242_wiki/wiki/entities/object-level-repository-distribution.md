---
title: Object-level repository distribution
type: value
id: '9.6'
status: rejected
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by: []
rejected_by:
- s01_p03
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
design_points:
- '[[designs/p021|P021]]'
tags:
- value
- rejected
- repository-storage-representation
---

# Object-level repository distribution

Distributes individual content-addressed objects across storage nodes rather than preserving repository-level packfile organization.

## Evidence

- **s01_p03** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …

## In design points

[[designs/p021|P021]]
