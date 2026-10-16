---
title: Git-and-rsync replication
type: value
id: '22.3'
status: accepted
dimension: '[[concepts/replica-synchronization-mechanism|Replica Synchronization Mechanism]]'
accepted_by:
- s03_p01
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- replica-synchronization-mechanism
---

# Git-and-rsync replication

Repository content is replicated using complementary Git and rsync mechanisms.

## Evidence

- **s03_p01** (accepts) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
