---
title: Foreground automatic garbage collection
type: value
id: '11.18'
status: rejected
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by:
- s05_p09
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p024|P024]]'
tags:
- value
- rejected
- repository-service-scaling
---

# Foreground automatic garbage collection

Runs repository garbage collection synchronously at command completion or threshold triggers.

## Evidence

- **s05_p09** (rejects) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …

## In design points

[[designs/p024|P024]]
