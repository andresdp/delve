---
title: Networked-filesystem repository access
type: value
id: '9.18'
status: outcome
dimension: '[[concepts/repository-storage-representation|Repository Storage Representation]]'
accepted_by: []
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-fs|GitHub filesystem distribution]]'
tags:
- value
- outcome
- repository-storage-representation
---

# Networked-filesystem repository access

The attempted networked-filesystem approach produces poor performance and buggy behavior because of mismatched filesystem assumptions.

## Evidence

- **s01_p04** (supports) · [[sources/s1|Git at any scale]] · GitHub and filesystems
  > A couple years after Git started to escape its Linux Kernel bubble, a scrappy startup was born in San Francisco. GitHub was founded in 2008 as a social coding platform with a very prescient tagline, "Git repository hosting: no longer a pain in the ass." I'm not joking here either, look it up. There was, all the way back in …
