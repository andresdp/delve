---
title: Majority-exclusive write locking
type: value
id: '6.17'
status: accepted
dimension: '[[concepts/write-commitment-and-consistency|Write Commitment and Consistency]]'
accepted_by:
- s03_p05
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
design_points:
- '[[designs/p008|P008]]'
- '[[designs/p021|P021]]'
tags:
- value
- accepted
- write-commitment-and-consistency
---

# Majority-exclusive write locking

Each write locks a majority exclusively so conflicting writes cannot both acquire a majority simultaneously.

## Evidence

- **s03_p05** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …

## In design points

[[designs/p008|P008]], [[designs/p021|P021]]
