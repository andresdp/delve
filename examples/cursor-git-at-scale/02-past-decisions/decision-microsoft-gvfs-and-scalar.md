---
title: "Decision: Microsoft scales Git by virtualizing the client, not the server"
category: past-decision
source: cursor.com/blog/git-at-any-scale
extra_sources:
  - github.com/microsoft/git/blob/vfs-2.37.3/contrib/scalar/docs/philosophy.md
  - devblogs.microsoft.com/devops/introducing-scalar
---

## Context

Where GitHub's Spokes attacks Git-at-scale as a *server replication* problem, Microsoft faced an
adjacent but different pain point: single monorepos (famously, the Windows OS repository, with on the
order of 90 million objects and around 100GB of compressed history) that were simply too large for an
ordinary developer machine to clone and work with comfortably, regardless of how well the server side
replicated them.

## The decision

Microsoft's answer was to change what the *client* has to download, not how the server replicates data.
The **GVFS protocol** (Git Virtual File System) lets a client fetch only commits and trees up front —
around 15GB instead of 100GB for the Windows repository — and pull individual file contents on demand as
they are actually touched, backed by cache servers placed near developers to keep that on-demand latency
low. **Scalar**, Microsoft's later and narrower tool, builds on the same idea using only mechanisms Git
itself now supports natively: partial clone (download only the objects needed for the current checkout),
sparse-checkout in "cone mode" (populate only the parts of the working tree currently being touched), and
background maintenance (hourly fetches, commit-graph and multi-pack-index updates) so the repository stays
current without blocking foreground work.

## Why the two efforts diverged, and what was deliberately dropped

Microsoft's own documentation is explicit that GVFS's original virtualization protocol was never intended
to become a permanent, upstream part of Git — it required a custom Git fork and dedicated cache-server
infrastructure, "relaxing" Git's purely distributed model by coupling clients to specific central
servers. Scalar was built to phase that out: rather than adding new machinery to Scalar itself, its
philosophy is to push improvements into upstream Git (partial clone, sparse-checkout, the multi-pack
index) and let Scalar only configure them, so that the special-purpose fork could eventually be retired
in favor of standard Git clients talking to standard Git hosts. This is a materially different point in
the design space from Spokes or Continuity: it optimizes what a single client needs to download and keep
warm, and leaves the question of how the *server* replicates and serves that data largely untouched.
