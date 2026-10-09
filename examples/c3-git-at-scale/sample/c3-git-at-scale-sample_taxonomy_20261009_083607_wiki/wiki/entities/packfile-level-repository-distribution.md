---
title: Packfile-level repository distribution
type: value
id: '5.35'
status: mixed
dimension: '[[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]'
accepted_by:
- s01_p02
- s05_p12
rejected_by:
- s01_p04
passages: 3
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p004|P004]]'
tags:
- value
- mixed
- git-hosting-and-acceleration-integration
---

# Packfile-level repository distribution

Packfiles rather than complete filesystems are distributed to scale repository access.

## Evidence

- **s01_p02** (accepts) · [[sources/s1|Git at any scale]] · What's hard about Git?
  > The challenge in hosting Git repositories at scale is inherent in the design of Git itself: a \*distributed\* version control system means that all instances of a repository are identical. There's nothing special about the repository on a Git server that doesn't apply to a repository on a developer's laptop. Although at first it may appear that this makes hosting …
- **s01_p04** (rejects) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
- **s05_p12** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[[designs/p004|P004]]
