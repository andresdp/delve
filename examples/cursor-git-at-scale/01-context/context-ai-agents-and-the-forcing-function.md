---
title: AI coding agents as the forcing function behind a new architecture
category: context
source: cursor.com/blog/git-at-any-scale
---

## Context

Architectural rewrites are expensive to justify, and GitHub's Spokes system had already served as the
industry's de facto answer to "how do you host Git at scale" for roughly thirteen years. Cursor's blog
post is explicit that what changed was not a flaw discovered in Spokes' design in isolation, but a shift
in *workload* that Spokes' assumptions were never built to absorb.

## What changed

Cursor builds an editor and platform where AI agents — not only humans — read, write, and operate on Git
repositories. That shifts the traffic profile in a way that stresses a replica-based architecture from
both ends at once:

- **Large, high-traffic monorepos** now see far more concurrent CI-driven read load than a purely
  human-paced workflow would generate, because agents can trigger builds, tests, and checks continuously
  rather than in the rhythm of a human workday.
- **A long tail of small, short-lived repositories** appears as agents spin up throwaway workspaces,
  scratch branches, or one-off experiments that may be touched once and then abandoned — repositories
  that need to exist safely and briefly, not permanently and expensively.

A replication scheme built around a small, fixed number of full replicas per repository (Spokes'
three-replica design) is well matched to a world of a bounded number of important, long-lived
repositories. It is poorly matched to a world where the *number* of repositories can grow by orders of
magnitude because most of them are agent-created and short-lived, while a shrinking minority are
monorepos whose read demand keeps climbing.

## Why this is a context document, not a decision

This document deliberately stays at the level of "why does the problem look different now," rather than
describing any specific technical choice. It is the shared backdrop against which every decision, every
tradeoff, and every alternative described elsewhere in this corpus should be read: Cursor is not solving
"how do we host Git" in the abstract, but "how do we host Git for a workload where the population of
repositories is enormous, heavily skewed, and driven substantially by non-human, high-frequency agents."
