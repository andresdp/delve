---
title: "Decision: Cursor replaces consensus with a write-ahead log in S3"
category: past-decision
source: cursor.com/blog/git-at-any-scale
extra_sources: [en.wikipedia.org/wiki/Rendezvous_hashing]
---

## Context

Spokes had proven, for over a decade, that replicating whole Git repositories with strong consistency
was viable — but its scaling knobs (a small fixed replica count, consensus-bound write latency) were the
wrong shape for a workload of both huge monorepos and millions of disposable, agent-created repositories.
Rather than tune Spokes' consensus parameters, Cursor's engineering team chose a different source of
truth altogether.

## The decision

Continuity makes S3-compatible object storage — not any disk-resident replica — the single, durable
source of truth for a repository, in the form of an append-only **write-ahead log (WAL)**: every push is
written to local NVMe *and* uploaded to S3 as its own numbered WAL entry, and only after the
corresponding reference transaction succeeds does an atomic compare-and-swap (CAS) update a small WAL
index object in S3 to point at it. A push is never acknowledged until this sequence is fully persisted,
which forces strict linearizability on every write without requiring any multi-node voting protocol.
Repositories on local disk are demoted to the status of a "warm cache": useful for latency, never
required for correctness, since any missing state can always be rematerialized from the WAL. Routing
which node should hold which repository is handled by rendezvous (highest-random-weight) hashing rather
than an external routing database, so there is no metadata store to keep consistent and no election
protocol to run when a node fails.

## What this decision explicitly gives up, and what it buys

Continuity gives up the constant-time, disk-to-disk consensus latency that 3PC offers when all replicas
are healthy and nearby, and accepts that every write's floor latency is now S3's write latency. In
exchange, it decouples replica count from correctness entirely: a repository can have one replica or a
hundred, replicas can be added or removed without a repair protocol, and any server can safely accept a
write for any repository because CAS against S3 — not agreement among peers — is what makes it safe.
This is the single decision from which nearly every other property described elsewhere in this corpus
(stateless routing, optimistic gossip replication, primary-only compaction, linear read scaling) follows.
