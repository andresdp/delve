---
title: Repository-data transformation
type: value
id: '9.15'
status: rejected
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by: []
rejected_by:
- s01_p06
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- rejected
- repository-storage-representation
---

# Repository-data transformation

Repository contents are transformed into a separate client-facing storage format.

## Evidence

- **s01_p06** (rejects) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes was originally developed at GitHub around 2013, and it has since become an industry standard. Most Git hosting services use a variant of the Spokes approach (application-level replication for Git repositories) in their architecture. The main reason Spokes has worked well for many years is that it made three fundamental choices that, over time, have been proven to be …
