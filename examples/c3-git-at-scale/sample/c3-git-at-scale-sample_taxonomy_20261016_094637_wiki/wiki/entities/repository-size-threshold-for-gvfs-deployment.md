---
type: Outcome
title: Repository-size threshold for GVFS deployment
description: Repository size and user population determine whether GVFS and cache-server infrastructure are warranted.
id: '6.3'
dimension: /concepts/large-repository-object-acquisition.md
accepted_by: []
rejected_by: []
passages: 1
systems:
- /synthesis/systems/ms-scalar.md
tags:
- value
- outcome
- large-repository-object-acquisition
stance: outcome
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Repository-size threshold for GVFS deployment

Repository size and user population determine whether GVFS and cache-server infrastructure are warranted.

## Evidence

- **s05_p03** (supports) · [Introducing Scalar](/sources/s5.md) · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
