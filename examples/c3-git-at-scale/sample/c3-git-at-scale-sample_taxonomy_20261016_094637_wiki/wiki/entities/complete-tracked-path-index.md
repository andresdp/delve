---
title: Complete tracked-path index
type: value
id: '9.14'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Complete tracked-path index

The client index records every tracked path to support core command state inspection.

## Evidence

- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …
