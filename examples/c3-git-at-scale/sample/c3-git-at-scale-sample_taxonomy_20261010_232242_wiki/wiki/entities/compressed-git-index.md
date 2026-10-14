---
title: Compressed Git index
type: value
id: '12.3'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s04_p02
- s05_p05
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p003|P003]]'
- '[[designs/p018|P018]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Compressed Git index

Index compression reduces client-side repository metadata size.

## Evidence

- **s04_p02** (accepts) · [[sources/s4|Scalar philosophy]]
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …

## In design points

[[designs/p003|P003]], [[designs/p018|P018]]
