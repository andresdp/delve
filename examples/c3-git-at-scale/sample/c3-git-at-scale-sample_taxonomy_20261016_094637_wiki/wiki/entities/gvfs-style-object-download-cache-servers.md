---
type: Design Alternative
title: GVFS-style object-download cache servers
description: Separate fetch-object endpoints deliver packfiles while branch-update authority remains on central repository services.
id: '6.5'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by:
- s05_p03
- s05_p15
rejected_by: []
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- accepted
- large-repository-object-acquisition
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# GVFS-style object-download cache servers

Separate fetch-object endpoints deliver packfiles while branch-update authority remains on central repository services.

## Evidence

- **s05_p03** (accepts) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p15** (accepts) · [Introducing Scalar](/sources/s5.md) · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
