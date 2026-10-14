---
title: Git status latency reduction
type: value
id: '12.43'
status: outcome
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- client-repository-and-working-tree-scaling
---

# Git status latency reduction

Lowering status latency by avoiding full working-directory inspection in very large repositories.

## Evidence

- **s05_p04** (supports) · [[sources/s5|Introducing Scalar]] · Quick start for using the GVFS protocol
  > When using \`scalar clone\`, the working directory contains only the files at root using the Git sparse-checkout feature in \*cone mode\*. You can expand the files in your working directory using the \`git sparse-checkout set\` command, or fully populate your working directory by running \`git sparse-checkout disable\`. \`\`\` $ cd scalar/src $ ls AuthoringTests.md Directory.Build.targets SECURITY.md global.json CONTRIBUTING.md License.md Scalar.ruleset …
- **s05_p07** (supports) · [[sources/s5|Introducing Scalar]] · Modified Size
  > The \*modified size\* is the number of paths in the working directory that differ from the version in the index. This includes all files that are untracked or ignored by Git. This size determines the minimum amount of work that Git must do to update the index and its caches during the core commands. Without assistance, Git needs to scan …
