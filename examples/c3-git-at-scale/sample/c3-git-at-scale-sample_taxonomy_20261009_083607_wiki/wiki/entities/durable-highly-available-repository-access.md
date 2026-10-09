---
title: Durable highly available repository access
type: value
id: '1.12'
status: outcome
dimension: '[[concepts/repository-replica-placement|Repository Replica Placement]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- repository-replica-placement
---

# Durable highly available repository access

Maintain repository and gist access despite server and network failures through replicated placement.

## Evidence

- **s03_p01** (supports) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
