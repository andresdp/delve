---
type: Design Alternative
title: Persistent Scalar dependency
description: Scalar remains a required long-term layer above Git for repository-scale client performance.
id: '9.12'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p02
rejected_by:
- s05_p14
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- mixed
- client-repository-performance-strategy
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Persistent Scalar dependency

Scalar remains a required long-term layer above Git for repository-scale client performance.

## Evidence

- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p14** (rejects) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
