---
type: Design Alternative
title: GVFS without cache infrastructure
description: GVFS deployment proceeds without the cache-server infrastructure required for scalable large-repository access.
id: '6.9'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by:
- s05_p03
- s05_p08
rejected_by:
- s01_p05
- s05_p03
passages: 3
systems:
- /synthesis/systems/gh-fs.md
- /synthesis/systems/ms-gvfs.md
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p009.md
tags:
- value
- mixed
- large-repository-object-acquisition
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# GVFS without cache infrastructure

GVFS deployment proceeds without the cache-server infrastructure required for scalable large-repository access.

## Evidence

- **s01_p05** (rejects) · [Git at any scale](/sources/s1.md) · GitHub and filesystems
  > Further attempts were made with (frankly, in retrospect, horrific) technologies that replicated the filesystem at the block level. A short-lived deployment with GFS. A longer-lived deployment based on DRBD. They all hit a wall. They were \*terrible\* to operate day to day, and they didn't make up for it with good performance. It all boils down to the design of …
- **s05_p03** (both) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p08** (accepts) · [Introducing Scalar](/sources/s5.md) · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[P009](/designs/p009.md)
