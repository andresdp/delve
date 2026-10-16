---
title: Parallel checkout processing
type: value
id: '9.7'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p04
- s05_p06
- s05_p15
rejected_by: []
passages: 3
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Parallel checkout processing

Checkout work is processed in parallel to address checkout becoming a bottleneck after virtualization removal.

## Evidence

- **s05_p04** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for using the GVFS protocol
  > When using \`scalar clone\`, the working directory contains only the files at root using the Git sparse-checkout feature in \*cone mode\*. You can expand the files in your working directory using the \`git sparse-checkout set\` command, or fully populate your working directory by running \`git sparse-checkout disable\`. \`\`\` $ cd scalar/src $ ls AuthoringTests.md Directory.Build.targets SECURITY.md global.json CONTRIBUTING.md License.md Scalar.ruleset …
- **s05_p06** (accepts) · [[sources/s5|Introducing Scalar]] · Populated size
  > How many paths in the index are actually in your working directory? This is normally equal to the number of tracked files in the index, but Git’s sparse-checkout feature can make it smaller. It takes a little bit of work to design your repository to work with sparse-checkout, but it can allow most developers to populate a fraction of the …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
