---
title: GitHub filesystem distribution
type: system
code: GH-FS
organization: GitHub
dimensions: 1
tags:
- system
---

# GitHub filesystem distribution

GitHub before Spokes: NFS, GFS and DRBD filesystem distribution, then single-copy RPC fileservers.

Values supported by passages whose primary system is `GH-FS` (passage → system map).

| Dimension | Values (passages) |
|---|---|
| [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]] | • [[entities/filesystem-level-repository-distribution|Filesystem-level repository distribution]] (1)<br>• [[entities/git-level-repository-access-redesign|Git-level repository access redesign]] (1)<br>• [[entities/horizontal-application-instance-scaling|Horizontal application-instance scaling]] (1)<br>• [[entities/network-filesystem-repository-hosting|Network-filesystem repository hosting]] (1)<br>• [[entities/packfile-level-repository-distribution|Packfile-level repository distribution]] (1)<br>• [[entities/rails-monolith-with-co-located-repositories|Rails monolith with co-located repositories]] (1) |
