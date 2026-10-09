---
title: Incremental repository maintenance
type: value
id: '4.14'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p03
- s05_p09
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Incremental repository maintenance

Maintaining repository data incrementally rather than rewriting it all at once.

## Evidence

- **s05_p03** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p09** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
