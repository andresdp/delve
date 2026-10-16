---
type: Design Alternative
title: Hourly background repository fetch
description: Background fetches keep local objects current without placing download work in foreground commands.
id: '9.18'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s04_p02
- s05_p11
rejected_by: []
passages: 2
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

# Hourly background repository fetch

Background fetches keep local objects current without placing download work in foreground commands.

## Evidence

- **s04_p02** (accepts) · [Scalar philosophy](/sources/s4.md)
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p11** (accepts) · [Introducing Scalar](/sources/s5.md) · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
