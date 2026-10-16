---
title: Preserved visible branch references during background fetch
type: value
id: '9.21'
status: accepted
dimension: '[[concepts/client-repository-performance-strategy|Client Repository Performance Strategy]]'
accepted_by:
- s05_p10
- s05_p11
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
design_points:
- '[[designs/p004|P004]]'
- '[[designs/p009|P009]]'
tags:
- value
- accepted
- client-repository-performance-strategy
---

# Preserved visible branch references during background fetch

Background fetching updates objects while leaving local and visible remote-tracking branches unchanged.

## Evidence

- **s05_p10** (accepts) · [[sources/s5|Introducing Scalar]] · Set recommended Git config settings
  > The config step updates your Git config settings to some recommended values. The config step runs in the background so that new versions of Scalar can update the registered repositories after install. As new config options are supported, we will update the list of settings accordingly. Some of the noteworthy config settings are: 1. We disable auto-GC by setting \`gc.auto=0\` …
- **s05_p11** (accepts) · [[sources/s5|Introducing Scalar]] · Fetch in the background
  > The fetch step runs \`git fetch\` about once an hour. This allows your local repository to keep its object database close to that of your remotes. This means that the time-consuming part of \`git fetch\` that downloads the new objects happens when you are not waiting for your command to complete. We intentionally do not change your local branches, including …

## In design points

[[designs/p004|P004]], [[designs/p009|P009]]
