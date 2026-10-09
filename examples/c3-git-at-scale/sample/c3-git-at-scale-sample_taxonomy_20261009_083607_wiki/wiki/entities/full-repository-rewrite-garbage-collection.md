---
title: Full repository rewrite garbage collection
type: value
id: '4.16'
status: rejected
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by:
- s05_p09
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- rejected
- client-repository-workload-scaling
---

# Full repository rewrite garbage collection

Rewriting the complete object store during garbage collection.

## Evidence

- **s05_p09** (rejects) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
