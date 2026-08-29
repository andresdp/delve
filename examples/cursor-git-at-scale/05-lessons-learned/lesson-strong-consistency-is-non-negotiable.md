---
title: "Lesson learned: Git clients cannot tolerate eventual consistency"
category: lessons-learned
source: cursor.com/blog/git-at-any-scale
---

## Context

Eventual consistency is a common, well-accepted tradeoff in many distributed systems: accept that
different replicas may briefly disagree, in exchange for higher availability or throughput, on the
assumption that clients can tolerate a short window of staleness. Cursor's article treats this option as
having been considered and explicitly rejected for Git specifically, not merely deprioritized as an
implementation detail.

## The lesson

A Git client that pushes a commit and then, moments later, fetches from a replica that has not yet
caught up will observe a repository state that appears to be missing history it just created — an
anomaly with no equivalent "please retry" affordance built into ordinary Git workflows, since Git clients
generally assume that once a push succeeds, the pushed state is simply real and permanent. The article
describes this class of anomaly as producing "sharp edges" for users and for internal systems alike,
whether the eventual-consistency window shows up on the client side (a developer's fetch) or the backend
side (an internal service reading a repository shortly after another service wrote to it). Because CI
systems, code review tooling, and now AI agents all treat "a push succeeded" as a hard signal they build
further automation on top of, even rare and brief inconsistency windows compound into confusing,
hard-to-reproduce failures downstream.

## Why this lesson shaped the whole redesign

This is presented as a hard constraint rather than one design preference among several: it is the reason
Continuity's write path never acknowledges a push until it is fully durable (uploaded to S3, referenced
in the WAL index, visible to any subsequent reader), even though this is precisely the design choice that
puts S3's own write latency on the critical path for every push. The broader, generalizable takeaway is
that some client populations have consistency requirements baked into their usage pattern so deeply that
loosening consistency is not actually a viable lever for improving performance — it just relocates the
problem to wherever the inconsistency next becomes visible.
