---
title: Hourly background fetch
type: value
id: '12.16'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s04_p02
- s05_p11
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Hourly background fetch

Remote objects are fetched periodically outside foreground commands while ordinary local and remote-tracking branches remain unchanged.

## Evidence

- **s04_p02** (accepts) · [[sources/s4|Scalar philosophy]]
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
