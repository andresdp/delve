---
title: Why Git is hard to distribute at server scale
category: context
source: cursor.com/blog/git-at-any-scale
---

## Context

Git was designed in 2005 for a specific distributed workload: every developer clones the full history
and works against a local, single-machine copy. Hosting Git as a *centralized* service — one that many
clients read from and write to concurrently, at the scale of tens of millions of repositories — asks the
format to do something it was never built for, and that mismatch is the root cause behind almost every
architectural decision described in this corpus.

## The core mismatch

Git repositories are stored on disk as **packfiles**: compressed collections of objects (blobs, trees,
commits) referenced by content-addressed hashes. The logical structure of a repository is a **directed
acyclic graph (DAG)** of commits, but the physical layout of objects inside a packfile bears no relation
to that graph — objects end up scattered across a file in whatever order the packing algorithm chose.
Reading a single logical unit of history therefore means following a chain of pointers, each one
requiring a fresh lookup into the packfile to learn where the *next* pointer leads.

On a single local disk this is a cheap random-access read. Across a network, each pointer-hop becomes a
round trip, and round trips at scale are what make naive distribution strategies collapse: a design that
looks correct on paper (spread the objects across many machines, spread the files across many disks)
turns out to be far too slow in practice, because it multiplies the number of network round trips needed
to satisfy a single `git clone` or `git fetch`.

## Why this matters beyond one company

Every approach described elsewhere in this corpus — distributing the filesystem, distributing the
objects through a key-value store, replicating whole repositories with a consensus protocol, or
replacing consensus with a write-ahead log — is best understood as a different answer to the same
question: *given that Git's on-disk format assumes local, low-latency, random access, how do you provide
that illusion when the actual data lives on more than one machine?* None of the approaches change Git's
wire protocol or on-disk packfile format itself; they differ only in where the "real" copy of the data
lives and how consistency is maintained between that copy and everything that serves reads and writes
against it.
