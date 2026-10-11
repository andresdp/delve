---
title: Background commit-graph maintenance
type: value
id: '12.17'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s04_p02
- s05_p01
- s05_p02
- s05_p10
- s05_p11
rejected_by: []
passages: 5
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Background commit-graph maintenance

Commit graphs and multi-pack indexes are updated asynchronously to keep large-history operations efficient.

## Evidence

- **s04_p02** (accepts) · [[sources/s4|Scalar philosophy]]
  > Using \`scalar register\` on an existing Git repository will give you these benefits: \* Additional compression of your \`.git/index\` file. \* Hourly background \`git fetch\` operations, keeping you in-sync with your remotes. \* Advanced data structures, such as the \`commit-graph\` and \`multi-pack-index\` are updated automatically in the background. \* If using macOS or Windows, then Scalar configures Git's builtin File …
- **s05_p01** (accepts) · [[sources/s5|Introducing Scalar]]
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p10** (accepts) · [[sources/s5|Introducing Scalar]] · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …
