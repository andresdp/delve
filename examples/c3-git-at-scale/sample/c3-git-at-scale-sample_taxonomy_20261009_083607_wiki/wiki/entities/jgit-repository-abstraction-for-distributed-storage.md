---
title: JGit repository abstraction for distributed storage
type: value
id: '5.37'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
design_points:
- '[[designs/p016|P016]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# JGit repository abstraction for distributed storage

A Git repository abstraction is retained while replacing packfile storage with a distributed object store.

## Evidence

- **s01_p03** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …

## In design points

[[designs/p016|P016]]
