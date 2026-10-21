---
type: Design Alternative
title: Git-and-rsync replication
description: Repository content is replicated using complementary Git and rsync mechanisms.
id: '22.3'
dimension: /concepts/replica-synchronization-mechanism.md
accepted_by:
- s03_p01
rejected_by: []
passages: 1
systems:
- /synthesis/systems/gh-spokes.md
tags:
- value
- accepted
- replica-synchronization-mechanism
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Git-and-rsync replication

Repository content is replicated using complementary Git and rsync mechanisms.

## Evidence

- **s03_p01** (accepts) · [Building resilience in Spokes](/sources/s3.md) · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
