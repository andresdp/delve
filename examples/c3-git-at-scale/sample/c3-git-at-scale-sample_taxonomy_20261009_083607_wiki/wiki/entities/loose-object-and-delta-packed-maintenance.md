---
title: Loose-object and delta-packed maintenance
type: value
id: '4.9'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p12
- s05_p13
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Loose-object and delta-packed maintenance

Use cleanup and delta-compressed pack storage to control object count, lookup cost, and disk usage.

## Evidence

- **s05_p12** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …
- **s05_p13** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up pack-files
  > However, there is still a problem. If we let the number of pack-files grow without bound, Git cannot hold file handles to all pack-files at once. Rewriting pack-files could also reduce space costs due to better delta encoding. To solve this problem, Scalar has a pack-file maintenance step which performs an \*incremental\* repack by selecting a batch of small pack-files …
