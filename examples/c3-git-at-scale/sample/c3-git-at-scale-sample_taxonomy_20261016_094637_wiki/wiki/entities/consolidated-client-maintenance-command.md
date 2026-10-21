---
type: Design Alternative
title: Consolidated client maintenance command
description: A single foreground command runs the repository maintenance steps together.
id: '9.23'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p03
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Consolidated client maintenance command

A single foreground command runs the repository maintenance steps together.

## Evidence

- **s05_p03** (accepts) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
