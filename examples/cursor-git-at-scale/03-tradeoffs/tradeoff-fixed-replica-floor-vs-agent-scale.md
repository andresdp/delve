---
title: "Tradeoff: a safe minimum replica count vs. the cost of millions of tiny repos"
category: tradeoff
source: cursor.com/blog/git-at-any-scale
---

## Context

Spokes' consensus protocol needs a quorum to tolerate failure safely, and in practice that means a
repository cannot safely run on fewer than three replicas without risking an unrecoverable loss of
quorum if even two of them become corrupted or unavailable at once. That floor is a deliberate safety
margin — and it becomes a direct cost problem once the population of repositories includes millions of
agent-created, barely-used ones.

## The tradeoff

Every repository, no matter how small or short-lived, costs at least three times its storage and
replication overhead under Spokes, because the three-replica floor is a correctness requirement, not a
tunable performance knob. A repository an AI agent creates for a single throwaway task, touched once and
never read again, still needs the same three-way replication as an actively developed monorepo serving
constant CI traffic. There is no way to "downscale" an idle repository to one replica without accepting
a real risk of data loss, because the whole quorum mechanism depends on that floor being maintained.

## Why this is specifically a scale-workload tradeoff

This tradeoff was invisible for most of Spokes' history because the population of repositories a company
like GitHub hosted was dominated by long-lived, actively used projects, where a fixed per-repository
replication overhead is a reasonable and largely amortized cost. It becomes acute only once a large
fraction of repositories are transient by design — the specific shift in workload described in this
corpus's context documents on AI agents. Cursor's Continuity system directly targets this tradeoff:
because correctness in Continuity comes from S3 (the WAL), not from a quorum of live replicas, a
repository can legitimately have zero warm local replicas most of the time and be materialized on demand
from the WAL the moment it is next touched — turning what was a fixed, unavoidable cost under Spokes into
an elastic one under Continuity.
