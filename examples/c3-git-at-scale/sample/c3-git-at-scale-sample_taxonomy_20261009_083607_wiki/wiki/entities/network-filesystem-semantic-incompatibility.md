---
title: Network-filesystem semantic incompatibility
type: value
id: '5.42'
status: outcome
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- outcome
- git-hosting-and-acceleration-integration
---

# Network-filesystem semantic incompatibility

Network filesystem locking, tearing, reading, and synchronization semantics cause slow and buggy Git operations.

## Evidence

- **s01_p04** (supports) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
