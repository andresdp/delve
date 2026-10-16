---
title: Working-directory inspection by core commands
type: value
id: '9.13'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p05
- s05_p07
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Working-directory inspection by core commands

Core Git commands inspect on-disk working-directory state as part of repository operations.

## Evidence

- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …
- **s05_p07** (accepts) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
