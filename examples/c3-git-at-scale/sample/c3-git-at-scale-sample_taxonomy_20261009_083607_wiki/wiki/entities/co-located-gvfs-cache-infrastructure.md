---
title: Co-located GVFS cache infrastructure
type: value
id: '5.27'
status: accepted
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s05_p03
- s05_p08
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p009|P009]]'
tags:
- value
- accepted
- git-hosting-and-acceleration-integration
---

# Co-located GVFS cache infrastructure

A cache server is deployed alongside repository infrastructure to serve GVFS requests for large user populations.

## Evidence

- **s05_p03** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …

## In design points

[[designs/p009|P009]]
