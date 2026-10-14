---
title: Sync-aware replica selection
type: value
id: '11.3'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s01_p07
- s02_p06
- s05_p05
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Sync-aware replica selection

Reads are routed to nearby replicas known to be sufficiently up to date.

## Evidence

- **s01_p07** (accepts) · [[sources/s1|Git at any scale]] · Spokes and Consistency
  > Spokes is a \*consensus-based\* distributed system. It works by storing several copies of your Git repository on different servers. Whenever you push new data, an orchestrator fans out your push so that every instance of your repository receives a copy. The "fan-out" is synchronized with a classic consensus algorithm called 3PC (three-phase commit) so that a push is only accepted …
- **s02_p06** (accepts) · [[sources/s2|Stretching Spokes]] · Prioritizing user-initiated updates
  > Even with all of these optimizations, a reference update still costs about a third of a second. This is fine in most situations. But in the case that we mentioned earlier, where an update to \`master\` might cause a cascade of more than a hundred bookkeeping reference updates, processing the updates could keep the repository busy for something like 30 …
- **s05_p05** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 1: Focus on the files that matter
  > The most common Git commands are \`git status\` to see what change are available, \`git add\` to stage those changes before committing, and \`git checkout\` to change your working directory to match a different version. We call these the \*core commands\*. Each core command inspects the working directory to see how Git’s view of the working directory agrees with what …
