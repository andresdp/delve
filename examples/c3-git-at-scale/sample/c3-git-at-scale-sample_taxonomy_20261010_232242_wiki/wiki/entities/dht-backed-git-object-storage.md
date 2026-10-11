---
title: DHT-backed Git object storage
type: value
id: '9.5'
status: mixed
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s02_p01
rejected_by:
- s01_p03
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
tags:
- value
- mixed
- repository-storage-representation
---

# DHT-backed Git object storage

Stores individual Git objects in a distributed hash table instead of repository packfiles.

## Evidence

- **s01_p03** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
- **s02_p01** (accepts) · [[sources/s2|Stretching Spokes]] · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
