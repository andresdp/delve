---
title: "Tradeoff: primary-only compaction trades replica CPU for replica bandwidth"
category: tradeoff
source: cursor.com/blog/git-at-any-scale
---

## Context

Git repositories need periodic **compaction** (repacking loose objects and small packfiles into larger,
more efficient ones) to stay fast to read and reasonable in size on disk. Under a consensus-replicated
design like Spokes, every replica is a live, independent Git repository, which raises the question of
where repacking work should happen and how its results get back into agreement across replicas.

## The tradeoff

Cursor's Continuity design makes a deliberate, asymmetric choice: only the primary replica ever performs
the CPU-intensive repacking work. The resulting, already-compacted packfiles are uploaded to S3 alongside
the write-ahead log, and every other replica simply *downloads* the pre-compacted result rather than
recomputing it locally. This trades network bandwidth (every replica pulls the same compacted packfiles)
for CPU time (no replica other than the primary spends cycles on repacking), and it also sidesteps an
entire class of coordination problem that a naive design would face — concurrent, independent repacking
on multiple replicas at once, which in a consensus-based system like Spokes has been observed to cause
failovers when maintenance operations on different nodes step on each other.

## Where the bottleneck moved to

This tradeoff is explicitly named in Cursor's article as still being an open problem rather than a fully
solved one: with the write path's original bottleneck (consensus latency) removed, the *new* limiting
factor on push throughput is the speed of on-disk Git compaction on the primary itself, not the network
or S3. Cursor reports roughly 120 pushes per second on S3 Standard and over 300 per second on S3 Express
One Zone — a large jump from switching S3 storage classes, which is itself evidence that compaction, not
networking, is now the dominant cost. The team describes actively exploring new on-disk data layouts
specifically to reduce compaction's impact, which is the clearest acknowledgment in the source material
that this tradeoff has been made deliberately, with eyes open, rather than being an accidental limitation
of the design.
