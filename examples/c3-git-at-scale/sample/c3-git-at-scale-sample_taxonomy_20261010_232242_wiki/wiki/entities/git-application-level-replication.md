---
title: Git application-level replication
type: value
id: '10.8'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s01_p01
- s01_p02
- s01_p07
- s02_p01
- s02_p02
- s03_p01
rejected_by: []
passages: 6
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# Git application-level replication

Repository replication operates on Git-aware updates rather than filesystem blocks.

## Evidence

- **s01_p01** (accepts) · [[sources/s1|Git at any scale]] · Git at any scale
  > Hosting Git repositories at scale is a nightmare. When Linus Torvalds designed the first version of \*the information manager from hell\* (that's actually the tagline for Git, look it up), he had a very specific use case in mind: his own. He wanted to replace BitKeeper, the distributed version control system that was being used to develop the Linux Kernel. …
- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p01** (accepts) · [[sources/s2|Stretching Spokes]] · Stretching Spokes
  > GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. Background: Spokes GitHub developed a system called… GitHub’s Spokes system stores multiple distributed copies of Git repositories. This article discusses how we got Spokes replication to span widely separated datacenters. GitHub developed a system called Spokes to …
- **s02_p02** (accepts) · [[sources/s2|Stretching Spokes]] · Distant replicas. What’s all the fuss?
  > Before Spokes, we used DRBD filesystem block-level replication to keep repositories duplicated. This system was very sensitive to latency, so we were forced to keep fileserver replicas right next to each other. This was obviously not ideal, and getting off of it was the motivation that drove the initial development of Spokes. As soon as we had Spokes running, we …
- **s03_p01** (accepts) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
