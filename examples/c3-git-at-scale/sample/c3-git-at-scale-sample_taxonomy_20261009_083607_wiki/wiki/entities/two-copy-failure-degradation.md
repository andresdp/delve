---
title: Two-copy failure degradation
type: value
id: '3.32'
status: outcome
dimension: '[[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- outcome
- replica-failure-repair-and-failover
---

# Two-copy failure degradation

Resulting state after sudden server loss, in which two surviving copies serve traffic but cannot tolerate another failure.

## Evidence

- **s03_p01** (supports) · [[sources/s3|Building resilience in Spokes]] · Building resilience in Spokes
  > Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository… Spokes is the replication system for the file servers where we store over 38 million Git repositories and over 36 million gists.It keeps at least three copies of every repository …
- **s03_p08** (supports) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > We don’t perform “chaos monkey” testing on the Spokes file servers, for the same reasons we prefer to quiesce them before rebooting them: to avoid interrupting long-running reads. That is, we do not reboot them randomly just to confirm that sudden, single-node failures are still (mostly) harmless. Instead of “chaos monkey” testing, we perform rolling reboots as needed, which accomplish …
