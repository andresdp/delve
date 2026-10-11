---
title: Git-protocol Scalar registration
type: value
id: '12.28'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p03
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Git-protocol Scalar registration

Using ordinary Git protocol access with Scalar registration when GVFS infrastructure is unavailable.

## Evidence

- **s05_p03** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
