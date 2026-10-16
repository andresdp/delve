---
type: Design Alternative
title: Untracked cache
description: Git caches untracked-directory information to reduce large-repository inspection work.
id: '9.16'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p05
rejected_by: []
passages: 1
systems:
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

# Untracked cache

Git caches untracked-directory information to reduce large-repository inspection work.

## Evidence

- **s05_p05** (accepts) · [Introducing Scalar](/sources/s5.md) · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …
