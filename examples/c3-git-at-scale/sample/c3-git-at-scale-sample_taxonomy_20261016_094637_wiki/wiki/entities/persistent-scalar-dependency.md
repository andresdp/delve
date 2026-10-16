---
title: Persistent Scalar dependency
type: value
id: '9.12'
status: mixed
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p02
rejected_by:
- s05_p14
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- mixed
- client-repository-performance-strategy
---

# Persistent Scalar dependency

Scalar remains a required long-term layer above Git for repository-scale client performance.

## Evidence

- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p14** (rejects) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
