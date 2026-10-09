---
title: Foreground automatic garbage collection
type: value
id: '4.15'
status: mixed
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p10
- s05_p15
rejected_by:
- s05_p09
passages: 3
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p001|P001]]'
tags:
- value
- mixed
- client-repository-workload-scaling
---

# Foreground automatic garbage collection

Running automatic garbage collection during user-facing Git commands.

## Evidence

- **s05_p09** (rejects) · [[sources/s5|Introducing Scalar]] · Lesson 3: Don’t wait for expensive operations
  > \*There is no free lunch\*. Large repositories require upkeep. We can’t make users wait, so we defer these operations to background processes. Git typically handles maintenance by running garbage collection (GC) with the \`git gc --auto\` command at the end of several common commands, like \`git commit\` and \`git fetch\`. Auto-GC checks your \`.git\` directory to see if certain thresholds …
- **s05_p10** (accepts) · [[sources/s5|Introducing Scalar]] · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p001|P001]]
