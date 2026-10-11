---
title: Packfile transfer burden
type: value
id: '11.56'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Packfile transfer burden

Requires network transfer of Git packfiles even when server-side storage uses another representation.

## Evidence

- **s01_p03** (supports) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
- **s05_p08** (supports) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
- **s05_p13** (supports) · [[sources/s5|Introducing Scalar]] · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …
