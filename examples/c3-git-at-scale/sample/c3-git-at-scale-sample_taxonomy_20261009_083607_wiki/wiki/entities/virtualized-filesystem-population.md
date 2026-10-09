---
title: Virtualized filesystem population
type: value
id: '4.23'
status: rejected
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by: []
rejected_by:
- s05_p15
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p021|P021]]'
tags:
- value
- rejected
- client-repository-workload-scaling
---

# Virtualized filesystem population

A virtualized filesystem delays populated-size costs and accelerates checkout by presenting files on demand.

## Evidence

- **s05_p15** (rejects) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## In design points

[[designs/p021|P021]]
