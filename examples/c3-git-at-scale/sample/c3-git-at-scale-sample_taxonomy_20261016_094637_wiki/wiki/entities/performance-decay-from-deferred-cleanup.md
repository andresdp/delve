---
type: Outcome
title: Performance decay from deferred cleanup
description: Disabling automatic cleanup without effective background maintenance causes object accumulation and gradual performance deterioration.
id: '9.27'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- outcome
- client-repository-performance-strategy
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Performance decay from deferred cleanup

Disabling automatic cleanup without effective background maintenance causes object accumulation and gradual performance deterioration.

## Evidence

- **s05_p09** (supports) · [Introducing Scalar](/sources/s5.md) · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
