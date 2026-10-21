---
title: "Decision: GitHub builds Spokes — consensus-replicated real Git repositories"
category: past-decision
source: cursor.com/blog/git-at-any-scale
extra_sources: [github.blog/engineering/infrastructure/stretching-spokes]
---

## Context

Having ruled out distributing the filesystem and distributing raw objects, GitHub converged on a third
option around 2013: stop trying to virtualize storage underneath Git, and instead replicate whole,
ordinary Git repositories — the same packfiles a developer's laptop would have — across a small number
of machines, keeping them synchronized with a consensus protocol. The result, Spokes, replaced an earlier
DRBD-based block-replication system that was too latency-sensitive to operate well over distance.

## The decision

Spokes makes three deliberate architectural choices: work at the level of whole packfiles rather than
individual objects; store each replica as a real, ordinary Git repository on fast local disk (NVMe); and
keep every replica in lockstep using a three-phase commit (3PC) consensus algorithm for the reference
transaction that actually publishes a push (the branch-pointer update), while the (larger) packfile
payload is distributed to all replicas first, outside of consensus. Because a commit is invisible until a
reference points to it, only that final, small reference update needs strong consensus — a deliberate
separation that keeps the expensive part of a push (bytes) outside the expensive part of consistency
(agreement).

## Why it worked, and for how long

This design gave GitHub strong consistency (no client ever observes a pushed commit that later becomes
unreachable), tolerance of single-node failure while a quorum survives, and full reuse of standard Git
tooling with no custom on-disk format. As GitHub scaled past roughly 70 million repositories, the same
consensus mechanism was extended for geo-replication — letting reads be served from a nearby replica —
by adding transactional reference updates upstream in Git itself, incremental checksums to verify replica
state cheaply, and priority queuing so user-facing pushes were not starved by internal bookkeeping
traffic. Under this design, Spokes stood as the de facto industry answer to Git-at-scale for
approximately thirteen years.
