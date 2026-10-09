---
title: GVFS protocol support in Scalar
type: value
id: '5.12'
status: mixed
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p03
- s04_p01
- s05_p03
- s05_p15
rejected_by:
- s04_p01
passages: 4
systems:
- '[[synthesis/systems/goog-dht|Google JGit on a DHT]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
merged_from:
- id: '5.17'
  label: GVFS protocol exclusion from standard Git
tags:
- value
- mixed
- git-hosting-and-acceleration-integration
---

# GVFS protocol support in Scalar

Keep GVFS protocol support in Scalar for services that provide it rather than making it a standard Git capability.

## Evidence

- **s01_p03** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > There are broadly three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself. Git is a content-addressable data store. All objects in a Git repository (blobs, trees, commits, etc) are keyed by the SHA-1 of their contents. This is something that intuitively maps very well to a distributed key-value …
- **s04_p01** (both) · [[sources/s4|Scalar philosophy]]
  > The Philosophy of Scalar ======================== The team building Scalar has opinions about Git performance. Scalar takes out the guesswork by automatically configuring your Git repositories to take advantage of the latest and greatest features. It is difficult to say that these are the absolute best settings for every repository, but these settings do work for some of the largest repositories …
- **s05_p03** (accepts) · [[sources/s5|Introducing Scalar]] · Quick start for existing repositories
  > These logs show the details from updating the Git commit-graph in the background, the equivalent of the \`scalar run commit-graph\` command. You can run maintenance in the foreground using the \`scalar run\` command. When given the \`all\` option, Scalar runs all maintenance steps in a single command: \`\`\` $ scalar run all Setting recommended config settings...Succeeded Fetching from remotes...Succeeded Updating …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …

## Merged from

- {'id': '5.17', 'label': 'GVFS protocol exclusion from standard Git'}
