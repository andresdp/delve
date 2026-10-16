---
type: Design Alternative
title: Packfile-based Git networking
description: Push and fetch operations transfer Git packfiles over the network.
id: '6.6'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by:
- s01_p02
- s01_p03
- s05_p03
rejected_by:
- s01_p05
passages: 4
systems:
- /synthesis/systems/gh-fs.md
- /synthesis/systems/goog-dht.md
- /synthesis/systems/ms-scalar.md
tags:
- value
- mixed
- large-repository-object-acquisition
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Packfile-based Git networking

Push and fetch operations transfer Git packfiles over the network.

## Evidence

- **s01_p02** (accepts) · [Git at any scale](/sources/s1.md) · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p03** (accepts) · [Git at any scale](/sources/s1.md) · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
- **s01_p05** (rejects) · [Git at any scale](/sources/s1.md) · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s05_p03** (accepts) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
