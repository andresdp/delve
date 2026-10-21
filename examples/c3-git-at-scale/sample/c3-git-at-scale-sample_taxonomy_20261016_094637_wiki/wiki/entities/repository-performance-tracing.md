---
type: Design Alternative
title: Repository performance tracing
description: Client and repository performance bottlenecks are identified through custom tracing and analysis of user feedback.
id: '9.3'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s01_p16
- s05_p01
- s05_p02
rejected_by: []
passages: 3
systems:
- /synthesis/systems/cur-cont.md
- /synthesis/systems/ms-scalar.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Repository performance tracing

Client and repository performance bottlenecks are identified through custom tracing and analysis of user feedback.

## Evidence

- **s01_p16** (accepts) · [Git at any scale](/sources/s1.md) · Origin
  > We are acutely aware of how important it is to host somebody's source code. I think everybody who reads and understands this blog post is just as aware of it. A company can grind to a halt if its developers cannot push or pull from its Git repositories. The productivity cost of five minutes of downtime in your CI system …
- **s05_p01** (accepts) · [Introducing Scalar](/sources/s5.md)
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
