---
title: User-suspendable background maintenance
type: value
id: '12.19'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p02
- s05_p09
- s05_p15
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# User-suspendable background maintenance

Automated repository maintenance can be paused or stopped by the user.

## Evidence

- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p09** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
