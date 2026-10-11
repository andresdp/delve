---
title: Transitional Scalar performance layer
type: value
id: '11.43'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s04_p01
- s05_p01
- s05_p03
- s05_p14
rejected_by: []
passages: 4
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Transitional Scalar performance layer

Using Scalar as an interim performance layer while equivalent scalability capabilities move into core Git.

## Evidence

- **s04_p01** (accepts) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p01** (accepts) · [[sources/s5|Introducing Scalar]]
  > Git is a \*distributed\* version control system, so by default each Git repository has a copy of all files in the entire history. Even moderately-sized teams can create thousands of commits adding hundreds of megabytes to the repository every month. As your repository grows, Git may struggle to manage all that data. Time spent waiting for \`git status\` to report …
- **s05_p03** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p14** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > We intentionally are making Scalar do \*less\* and investing in making Git do \*more\*. Scalar is simply a way to get the performance we need today. As Git improves, Scalar can provide a way to transition away from needing Scalar and using only the core Git client. Scalar also serves as an example for the kinds of features we need …
