---
title: "Lesson learned: consensus replicas turn repositories into 'pets, not cattle'"
category: lessons-learned
source: cursor.com/blog/git-at-any-scale
---

## Context

"Pets, not cattle" is a well-known distributed-systems aphorism: infrastructure you name, monitor
individually, and nurse back to health when it breaks (a pet) versus infrastructure you can freely
destroy and replace without ceremony (cattle). Cursor's article applies this directly to what running
Spokes at scale is actually like operationally, independent of its consensus-latency limitations already
covered elsewhere in this corpus.

## The lesson

Because each repository under Spokes lives as a specific, identical set of replicas on specific machines,
tracked in a routing database, every repository becomes something that must be individually watched: its
replicas must be continuously checksummed to detect silent corruption, any detected divergence must be
repaired quickly (because losing a second replica while one is already unhealthy risks losing quorum
entirely and blocking pushes), and the routing metadata describing where a repository's replicas
currently live must itself stay available and correct. None of this is a single point of failure in the
traditional sense — Spokes tolerates individual node failures gracefully — but the aggregate operational
burden of keeping millions of individually-tracked, individually-repaired repositories healthy is real
and grows with the repository count, not just with traffic.

## Why this lesson outlasts the specific numbers

The three-phase-commit latency tradeoff (documented separately in this corpus) is a performance argument;
this one is an operations argument, and it is the reason Cursor frames Continuity's stateless design —
where a "missing" repository is not an incident but simply an on-demand rematerialization from the WAL —
as being as much about reducing operational toil as about improving throughput. The generalizable
takeaway the article draws is that any design requiring per-entity tracked state at very large entity
counts will eventually be constrained by the cost of *operating* that tracked state, regardless of how
well the underlying consensus or replication algorithm itself performs.
