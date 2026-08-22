---
title: "Evolution timeline: two decades of Git-hosting architecture"
category: evolution
source: cursor.com/blog/git-at-any-scale
extra_sources: [github.blog/engineering/infrastructure/stretching-spokes]
---

## Context

The decisions and tradeoffs described throughout this corpus did not happen simultaneously or in a
vacuum; they form a rough chronological sequence, each step responding to limits the previous step had
already exposed. This document lays out that sequence as a timeline, without asserting exact dates where
the source material does not give them.

## The sequence

1. **2005 — Git's original design.** Built for a fully distributed workload (every developer clones
   everything locally); centralized, multi-writer hosting was never a first-class design goal.
2. **Early GitHub — filesystem distribution.** NFS, GFS, and DRBD deployed underneath an unmodified Git
   and Rails application; abandoned once packfiles' random-access pattern proved too costly over a
   network and DRBD proved too operationally fragile over distance.
3. **Alongside — the distributed key-value-store attempt.** Google's JGit-based experiment with a
   distributed hash table for objects; technically feasible for storage but abandoned once
   graph-traversal round trips made clone performance impractical.
4. **~2013 — GitHub ships Spokes.** Whole-repository replication with three-phase-commit consensus,
   deliberately separating packfile distribution from reference-transaction consensus; becomes the
   de facto industry standard.
5. **Post-2013 — Spokes matures for geo-replication.** As GitHub passes roughly 70 million repositories,
   transactional reference updates, incremental checksums, and priority queuing are added to keep
   consensus latency manageable across continental distances (60–80ms round trips).
6. **In parallel — Microsoft addresses a different axis.** GVFS and later Scalar tackle monorepo size on
   the client side (partial clone, sparse-checkout, on-demand object fetch), leaving server-side
   replication design untouched and eventually favoring upstream Git features over a custom fork.
7. **Present day — AI agents change the workload.** Repository counts grow by orders of magnitude via
   short-lived, agent-created repositories, while CI-driven read load on large monorepos keeps climbing —
   exposing both of Spokes' scaling limits (tail-at-scale write latency, a fixed replica-count floor) at
   once.
8. **Cursor ships Continuity, then Origin.** A write-ahead log in S3 replaces consensus as the source of
   truth; disk replicas become disposable caches; Origin is the resulting production Git-hosting platform.

## Why the sequence matters as a whole

Read end to end, the timeline shows a recognizable pattern: each architecture solved the scaling problem
its predecessor's users were actually running into, at the cost of introducing a new, previously-hidden
constraint (packfile I/O patterns → graph traversal round trips → consensus tail latency and replica-count
rigidity → S3 write latency and on-disk compaction speed) — which is itself a lesson about how scaling
problems in this domain tend to move rather than disappear.
