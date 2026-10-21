---
type: Design Alternative
title: Automatic repository registration
description: Newly cloned repositories are automatically registered for recommended configuration and ongoing maintenance.
id: '9.24'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p02
- s05_p03
- s05_p10
rejected_by: []
passages: 3
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

# Automatic repository registration

Newly cloned repositories are automatically registered for recommended configuration and ongoing maintenance.

## Evidence

- **s05_p02** (accepts) · [Introducing Scalar](/sources/s5.md)
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p03** (accepts) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p10** (accepts) · [Introducing Scalar](/sources/s5.md) · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
