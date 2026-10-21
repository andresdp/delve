---
title: "Tradeoff: strong consensus vs. tail-at-scale write latency (Spokes)"
category: tradeoff
source: cursor.com/blog/git-at-any-scale
---

## Context

Spokes' three-phase commit guarantees that a reference update is durably agreed by every replica before
a push is acknowledged. That guarantee is exactly what makes Spokes safe to read from any replica — but
the same protocol is also the source of its most serious scaling limitation.

## The tradeoff

Any consensus protocol that must hear back from every participant (or a quorum of them) before
proceeding is only as fast as its slowest participant on that round — a phenomenon generally known as
"tail at scale." For Spokes, this means push latency is bound by whichever replica is currently slowest,
whether due to load, disk contention, or network conditions. Adding more replicas does not help
throughput; it makes the tail-latency problem worse, because each additional replica is one more chance
for the current round to be delayed by a slow participant. Cursor's article frames this plainly: the
system was designed around three replicas being enough, and pushing beyond that threshold causes
performance to degrade rather than improve.

## Why this could not simply be tuned away

The tradeoff is structural, not a matter of insufficient engineering effort: consensus protocols
purchase strong consistency precisely by requiring coordinated agreement, and coordinated agreement is
inherently vulnerable to its slowest member. GitHub's own later work on Spokes (adding transactional
reference updates, incremental checksums, and priority queuing) reduced the *constant* cost of each
round of consensus — it did not remove the dependency on the slowest replica. This is the specific cost
that large modern monorepos, needing many more than three replicas to absorb CI load, run directly into:
the very property (more replicas) that would help with read and CI capacity actively hurts write
throughput under a consensus-bound design. Cursor's Continuity system resolves this tradeoff not by
optimizing three-phase commit further, but by removing the requirement for multi-node consensus
entirely, at the cost of depending on S3's own write latency as the new floor (see the corresponding
decision document on Continuity's WAL design).
