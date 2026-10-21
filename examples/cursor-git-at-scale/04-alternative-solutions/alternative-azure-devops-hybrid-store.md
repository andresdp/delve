---
title: "Alternative considered and rejected: blob storage plus a relational database"
category: alternative-solutions
source: cursor.com/blog/git-at-any-scale
---

## Context

When justifying why Continuity's write-ahead log is itself the single source of truth — rather than one
input into a larger system that also depends on an external database — Cursor's article explicitly
contrasts its choice with a different, hybrid architecture it attributes to Azure DevOps: pairing object
(blob) storage for the actual Git data with a separate relational database that tracks metadata,
consistency state, or both.

## The alternative

In a hybrid blob-plus-database design, the object store holds the bulk data (packfiles, objects) while a
relational database is responsible for the bookkeeping a Git host needs on top of that: which objects
belong to which repository, what the current state of each reference is, and potentially transactional
guarantees that the blob store alone cannot provide. This is a common and well-understood pattern in
systems design generally — separate the cheap, bulk storage of large immutable blobs from the smaller,
frequently-updated, transactionally-sensitive metadata that describes them.

## Why Cursor's article argues against it for this problem

The article's objection is not that the hybrid pattern is unsound in general, but that it reintroduces
exactly the kind of external dependency and consistency-coordination problem that motivated moving away
from Spokes' routing databases in the first place: a relational database sitting alongside the blob store
becomes a second source of truth that must be kept consistent with the first, and now failure modes
include the two disagreeing with each other. Continuity's alternative claim is that the WAL, on its own,
can serve as *both* the bulk data store and the ordering/consistency mechanism, because each WAL entry is
already ordered, immutable, and verifiable via S3's own conditional-request (ETag) semantics — removing
the need for a second system to track state that the log already encodes. Whether this fully generalizes
to every Git-hosting workload is left implicit in the source material; what is explicit is that Cursor
weighed the hybrid pattern and chose to avoid the operational surface area of a second, separately
consistent metadata store.
