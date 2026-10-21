---
title: "Evolution of thinking: from 'agree before you act' to 'log first, derive truth after'"
category: evolution
source: cursor.com/blog/git-at-any-scale
---

## Context

Beyond any single technical decision, Cursor's article traces a shift in the *mental model* used to
reason about distributed Git storage — a shift that mirrors a broader pattern seen elsewhere in
distributed-systems history (event sourcing, log-structured databases, and blockchain-style ledgers all
share a family resemblance to it), applied here specifically to Git.

## The earlier model: consensus as the source of correctness

Spokes' three-phase commit embodies a "agree before you act" philosophy: correctness comes from getting
multiple parties to explicitly vote and confirm a state transition before it is considered to have
happened. Under this model, "the current state of a repository" is defined operationally as *whatever a
quorum of replicas currently agree it is* — there is no single, canonical record independent of the
replicas themselves, which is exactly why losing too many replicas at once (quorum loss) is catastrophic:
without a quorum, there is no way left to determine what the true state even is.

## The later model: an immutable log as the source of correctness

Continuity inverts this: correctness comes from *recording* a fact (a push) durably and immutably in one
place first (the WAL in S3), and every other question — what does replica X currently look like, is
replica Y up to date, what should a new node materialize — is answered by comparing against that log
rather than by negotiating with peers. Under this model, "the current state of a repository" has a
single, well-defined answer at all times (the latest WAL index entry), and any replica, including one
that has never held a single byte of the repository before, can derive a fully correct copy simply by
reading the log. Quorum loss stops being a meaningful failure mode, because there is no quorum to lose —
disk replicas are demoted from being co-owners of the truth to being caches of it.

## What generalizes from this shift

The article frames this less as "logs are better than consensus" in the abstract, and more as a case
where the earlier model was the right fit for a smaller, more homogeneous population of repositories, and
the later model became necessary once the population grew large and heterogeneous enough (see this
corpus's context documents on AI agents) that per-repository, per-replica coordination became the binding
constraint rather than raw throughput.
