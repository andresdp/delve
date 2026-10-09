---
title: Suppressed ahead-behind status calculation
type: value
id: '4.22'
status: accepted
dimension: '[[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]'
accepted_by:
- s05_p10
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p013|P013]]'
tags:
- value
- accepted
- client-repository-workload-scaling
---

# Suppressed ahead-behind status calculation

Status omits branch ahead-behind comparison to reduce repeated command latency.

## Evidence

- **s05_p10** (accepts) · [[sources/s5|Introducing Scalar]] · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …

## In design points

[[designs/p013|P013]]
