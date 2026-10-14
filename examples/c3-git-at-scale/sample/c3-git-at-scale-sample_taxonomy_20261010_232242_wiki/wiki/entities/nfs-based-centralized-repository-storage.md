---
title: NFS-based centralized repository storage
type: value
id: '9.4'
status: rejected
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by: []
rejected_by:
- s01_p04
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- rejected
- repository-storage-representation
---

# NFS-based centralized repository storage

NFS is considered for centralized storage but rejected because Git's local-filesystem assumptions do not work safely or efficiently over it.

## Evidence

- **s01_p04** (rejects) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
