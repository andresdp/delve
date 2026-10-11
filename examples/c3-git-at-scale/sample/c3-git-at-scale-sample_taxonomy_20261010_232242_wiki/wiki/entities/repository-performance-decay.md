---
title: Repository performance decay
type: value
id: '11.54'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- repository-service-scaling
---

# Repository performance decay

Gradually degrades Git performance as new objects accumulate without maintenance.

## Evidence

- **s05_p09** (supports) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
