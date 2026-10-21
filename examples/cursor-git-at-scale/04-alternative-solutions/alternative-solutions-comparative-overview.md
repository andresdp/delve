---
title: "Alternative solutions, compared: five answers to one question"
category: alternative-solutions
source: cursor.com/blog/git-at-any-scale
---

## Context

Across its history, Git-at-scale has been attempted along at least five distinct axes, each optimizing
for a different part of the problem and each accepting a different cost. Laying them side by side (as
this document does, without ranking them or naming any of this as a formal "dimension") makes clear that
they are not simply better-or-worse versions of the same idea — they intervene at different layers of
the stack entirely.

## The five approaches

- **Distribute the filesystem** (early GitHub: NFS, GFS, DRBD) — intervenes below Git, at the storage
  layer, trying to make several disks look like one. Optimizes for leaving Git and the application
  untouched; defeated by Git's assumption of true local-disk semantics and by packfiles' scattered,
  random-access layout.
- **Distribute the objects** (Google/JGit: a distributed hash table) — intervenes at the object-storage
  layer, replacing packfiles with a key-value store. Optimizes for independent, elastic storage scaling;
  defeated by the DAG's need for sequential, one-hop-at-a-time traversal, which turns every graph walk
  into a chain of network round trips.
- **Replicate whole repositories with consensus** (GitHub's Spokes) — intervenes at the whole-repository
  level, keeping ordinary Git repos in sync via three-phase commit. Optimizes for strong consistency and
  full compatibility with unmodified Git tooling; defeated, at very large scale, by tail-at-scale write
  latency and a replica-count floor mismatched to a workload with millions of disposable repositories.
- **Virtualize the client** (Microsoft's GVFS and Scalar) — intervenes at the client's checkout and
  fetch behavior rather than the server's replication strategy, downloading only what is needed and
  fetching the rest on demand. Optimizes for making one enormous monorepo usable on an ordinary
  developer machine; does not, by itself, address how the server replicates or serves that data at all.
- **Replace consensus with a log** (Cursor's Continuity) — intervenes at the level of what "the source
  of truth" even means, replacing a quorum of live disk replicas with an immutable, S3-resident
  write-ahead log. Optimizes for elastic replica counts and linear read scaling; its new cost center is
  S3 write latency and on-disk compaction speed, rather than consensus.

## Why the ordering above is not "improvement": it is "trajectory"

None of these approaches obsoletes the others in a strict sense — GVFS/Scalar's client-side virtualization
and Continuity's server-side log-based replication solve adjacent, not identical, problems, and a real
system could plausibly combine both. What connects all five, and what makes this corpus interesting
material for design-space mining, is that each one is a considered response to a specific, named failure
of the one before it (or beside it), not an arbitrary design preference.
