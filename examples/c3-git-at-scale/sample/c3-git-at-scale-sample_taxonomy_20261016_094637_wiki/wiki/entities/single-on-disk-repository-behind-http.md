---
type: Design Alternative
title: Single on-disk repository behind HTTP
description: An HTTP frontend serves one conventional on-disk repository from a single host.
id: '13.9'
dimension: /concepts/repository-placement-and-read-routing.md
accepted_by: []
rejected_by:
- s01_p02
passages: 1
systems: []
tags:
- value
- rejected
- repository-placement-and-read-routing
stance: rejected
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Single on-disk repository behind HTTP

An HTTP frontend serves one conventional on-disk repository from a single host.

## Evidence

- **s01_p02** (rejects) · [Git at any scale](/sources/s1.md) · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
