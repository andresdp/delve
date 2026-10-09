---
title: GVFS without cache infrastructure
type: value
id: '5.29'
status: rejected
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by: []
rejected_by:
- s05_p03
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p013|P013]]'
tags:
- value
- rejected
- git-hosting-and-acceleration-integration
---

# GVFS without cache infrastructure

GVFS is adopted without the cache-server infrastructure needed to support its scalable request model.

## Evidence

- **s05_p03** (rejects) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …

## In design points

[[designs/p013|P013]]
