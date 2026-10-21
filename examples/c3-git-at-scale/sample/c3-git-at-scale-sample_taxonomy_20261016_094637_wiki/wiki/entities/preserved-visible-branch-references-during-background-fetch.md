---
type: Design Alternative
title: Preserved visible branch references during background fetch
description: Background fetching updates objects while leaving local and visible remote-tracking branches unchanged.
id: '9.21'
dimension: /concepts/client-repository-performance-strategy.md
accepted_by:
- s05_p10
- s05_p11
rejected_by: []
passages: 2
systems:
- /synthesis/systems/ms-scalar.md
design_points:
- /designs/p004.md
- /designs/p009.md
tags:
- value
- accepted
- client-repository-performance-strategy
stance: accepted
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

# Preserved visible branch references during background fetch

Background fetching updates objects while leaving local and visible remote-tracking branches unchanged.

## Evidence

- **s05_p10** (accepts) · [Introducing Scalar](/sources/s5.md) · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
- **s05_p11** (accepts) · [Introducing Scalar](/sources/s5.md) · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[P004](/designs/p004.md), [P009](/designs/p009.md)
