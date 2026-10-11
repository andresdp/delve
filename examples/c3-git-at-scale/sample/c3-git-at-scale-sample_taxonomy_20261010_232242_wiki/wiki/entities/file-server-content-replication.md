---
title: File-server content replication
type: value
id: '10.22'
status: accepted
dimension: '[[concepts/replica-topology-and-persistence|Replica Topology and Persistence]]'
accepted_by:
- s03_p01
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-topology-and-persistence
---

# File-server content replication

Replicating repository and gist content stored on file servers across the application’s server fleet.

## Evidence

- **s03_p01** (accepts) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
