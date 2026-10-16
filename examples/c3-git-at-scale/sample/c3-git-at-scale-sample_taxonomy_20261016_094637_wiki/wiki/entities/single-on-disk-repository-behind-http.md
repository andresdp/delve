---
title: Single on-disk repository behind HTTP
type: value
id: '13.9'
status: rejected
dimension: '[[concepts/repository-placement-and-read-routing|Repository Placement and Read Routing]]'
accepted_by: []
rejected_by:
- s01_p02
passages: 1
systems: []
tags:
- value
- rejected
- repository-placement-and-read-routing
---

# Single on-disk repository behind HTTP

An HTTP frontend serves one conventional on-disk repository from a single host.

## Evidence

- **s01_p02** (rejects) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
