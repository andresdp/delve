---
title: "Decision (rejected): store Git objects in a distributed key-value store"
category: past-decision
source: cursor.com/blog/git-at-any-scale
---

## Context

After filesystem-level distribution proved unworkable, a second and conceptually more elegant idea
followed a different layer entirely: since every Git object is already content-addressed by its SHA-1
hash, why not treat a repository as nothing more than a very large key-value map, and let a distributed
hash table hold it?

## The decision

Engineers working with JGit (the Java implementation of Git) built a version of this idea: repository
storage was abstracted so that packfile access could be replaced by lookups against a distributed
hash table, decoupling "where the bytes live" from "how Git reads them." Google is named as having
pursued this direction.

## Why it was attractive

Content-addressable storage is exactly what distributed key-value stores are good at, and the approach
promised to scale storage independently of any single machine, fetching any object from any node without
depending on local filesystem semantics at all — sidestepping the exact problem that killed the
filesystem-distribution attempt.

## Why it was abandoned

Git repositories are not flat maps; they are graphs. A commit points to a tree, a tree points to blobs
and other trees, and none of those pointers can be resolved in advance — the traversal has to happen one
hop at a time, because you cannot know the address of the next object until you have already fetched the
current one. Against a local disk this costs a cheap sequence of reads; against a distributed store, each
hop becomes a network round trip, and typical Git operations require many hops. On top of that, Git's
network protocol still requires transferring data to clients in packfile form regardless of how it is
stored server-side, so the distributed store would have had to reconstruct packfiles on every request
rather than simply exposing bytes as-is. In practice, clone performance degraded so much that the design
was abandoned despite being technically feasible — a clear instance of a solution that was correct in
principle but was defeated by the graph-shaped access pattern Git operations actually exhibit.
