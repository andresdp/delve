---
title: On-demand object retrieval
type: value
id: '12.6'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p04
- s05_p08
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# On-demand object retrieval

Fetch repository objects dynamically when clients need them instead of transferring the complete object history initially.

## Evidence

- **s05_p04** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for using the GVFS protocol
  > When using \`scalar clone\`, the working directory contains only the files at root using the Git sparse-checkout feature in \*cone mode\*. You can expand the files in your working directory using the \`git sparse-checkout set\` command, or fully populate your working directory by running \`git sparse-checkout disable\`. \`\`\` $ cd scalar/src $ ls AuthoringTests.md Directory.Build.targets SECURITY.md global.json CONTRIBUTING.md License.md Scalar.ruleset …
- **s05_p08** (accepts) · [[sources/s5|Introducing Scalar]] · Lesson 2: Reduce object transfer
  > Now that the working directory is under control, let’s investigate another expensive dimension of Git at scale. Git expects a complete copy of all objects, both currently referenced and all versions in history. This can be a massive amount of data to transfer — especially when you only need objects near your current branch do a checkout and get on …
