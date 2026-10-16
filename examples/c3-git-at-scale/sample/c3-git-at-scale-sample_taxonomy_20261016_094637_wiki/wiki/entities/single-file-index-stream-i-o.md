---
title: Single-file index stream I/O
type: value
id: '9.17'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p019|P019]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Single-file index stream I/O

Index data is streamed through one file with cost dominated by sequential file I/O.

## Evidence

- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …

## In design points

[[designs/p019|P019]]
