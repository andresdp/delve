---
title: "Decision (rejected): distribute the filesystem underneath Git"
category: past-decision
source: cursor.com/blog/git-at-any-scale
---

## Context

Faced with the need to serve Git repositories from more than one machine, GitHub's earliest scaling
attempts tried to leave Git itself, and the application code sitting on top of it, completely untouched.
Instead, they attacked the problem one layer down: make the *filesystem* distributed, and let Git go on
believing it was talking to an ordinary local disk.

## The decision

GitHub deployed standard distributed-storage technology — network filesystems (NFS), distributed
filesystems (GFS), and block-level replication (DRBD) — underneath its Rails application, so that
multiple servers could see the same repository data without any change to how Git or the application
read and wrote it.

## Why it was attractive

The appeal was architectural minimalism: no fork of Git, no new wire protocol, no rewritten application
layer. If the filesystem could be made to look local everywhere, every other layer of the stack could
stay exactly as it was.

## Why it was abandoned

Git's on-disk format assumes filesystem semantics that only hold true on a local disk: precise locking
behavior, atomic writes, and low-latency random access to arbitrary offsets inside large packfiles.
Network filesystems could not reproduce those guarantees without severe performance penalties, and
block-level replication like DRBD proved to be "extremely difficult to operate" in practice, forcing
replicas to stay close together to avoid latency-sensitive failures. The specific failure mode was
structural rather than incidental: because packfile objects are scattered with no relationship to the
logical commit graph, satisfying a single Git operation means many small random reads, and turning any of
those reads into a network hop (rather than a local disk seek) multiplies latency far past what the
system could tolerate at GitHub's scale. This is the decision that later motivated moving the replication
problem up a layer, to the level of whole Git repositories rather than raw filesystem blocks — a
threshold that eventually led to Spokes.
