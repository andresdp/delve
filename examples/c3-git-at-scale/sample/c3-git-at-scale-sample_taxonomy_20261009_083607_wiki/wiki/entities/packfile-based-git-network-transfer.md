---
title: Packfile-based Git network transfer
type: value
id: '5.23'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p02
- s01_p03
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# Packfile-based Git network transfer

Using packfiles as the Git protocol's network transfer representation.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p03** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
