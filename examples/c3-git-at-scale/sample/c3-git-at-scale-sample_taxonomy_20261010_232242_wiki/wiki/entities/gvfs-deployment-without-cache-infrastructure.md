---
title: GVFS deployment without cache infrastructure
type: value
id: '12.27'
status: mixed
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p03
rejected_by:
- s05_p03
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p008|P008]]'
tags:
- value
- mixed
- client-repository-and-working-tree-scaling
---

# GVFS deployment without cache infrastructure

Whether GVFS is deployed without the cache-server infrastructure required for sufficiently large repositories.

## Evidence

- **s05_p03** (both) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …

## In design points

[[designs/p008|P008]]
