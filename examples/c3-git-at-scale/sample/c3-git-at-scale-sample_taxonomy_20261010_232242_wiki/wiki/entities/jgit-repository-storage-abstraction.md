---
title: JGit repository-storage abstraction
type: value
id: '9.7'
status: accepted
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by:
- s01_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
design_points:
- '[[designs/p017|P017]]'
tags:
- value
- accepted
- repository-storage-representation
---

# JGit repository-storage abstraction

Uses replaceable JGit storage interfaces to change repository storage while retaining Git operations.

## Evidence

- **s01_p03** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …

## In design points

[[designs/p017|P017]]
