---
title: Ahead/behind calculation suppression
type: value
id: '12.24'
status: accepted
dimension: '[[concepts/client-repository-and-working-tree-scaling|Client Repository and Working-Tree Scaling]]'
accepted_by:
- s05_p10
rejected_by: []
passages: 1
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- client-repository-and-working-tree-scaling
---

# Ahead/behind calculation suppression

Interactive status omits expensive ahead/behind comparison.

## Evidence

- **s05_p10** (accepts) · [[sources/s5|Introducing Scalar]] · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
