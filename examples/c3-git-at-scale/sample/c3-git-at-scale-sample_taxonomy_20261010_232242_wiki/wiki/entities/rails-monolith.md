---
title: Rails monolith
type: value
id: '12.5'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s01_p04
- s05_p08
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
design_points:
- '[[designs/p005|P005]]'
- '[[designs/p011|P011]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Rails monolith

The application begins and largely remains a Rails monolith around repository access.

## Evidence

- **s01_p04** (accepts) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[[designs/p005|P005]], [[designs/p011|P011]]
