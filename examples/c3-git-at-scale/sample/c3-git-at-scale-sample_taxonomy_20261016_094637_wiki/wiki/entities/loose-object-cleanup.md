---
title: Loose-object cleanup
type: value
id: '12.3'
status: accepted
dimension: '[[concepts/compaction-maintenance-technique|Compaction Maintenance Technique]]'
accepted_by:
- s05_p12
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p007|P007]]'
- '[[designs/p008|P008]]'
- '[[designs/p010|P010]]'
- '[[designs/p020|P020]]'
tags:
- value
- accepted
- compaction-maintenance-technique
---

# Loose-object cleanup

Maintenance removes accumulated loose-object storage to reduce disk and lookup overhead.

## Evidence

- **s05_p12** (accepts) · [[sources/s5|Introducing Scalar]] · Clean up loose objects
  > As you work, Git creates “loose” objects by writing the data of a single object to a file named according to its SHA-1 hash. This is very quick to create, but accumulating too many objects like this can have significant performance drawbacks. It also uses more disk space than necessary, since Git’s pack-files can compress data more efficiently using delta …

## In design points

[[designs/p007|P007]], [[designs/p008|P008]], [[designs/p010|P010]], [[designs/p020|P020]]
