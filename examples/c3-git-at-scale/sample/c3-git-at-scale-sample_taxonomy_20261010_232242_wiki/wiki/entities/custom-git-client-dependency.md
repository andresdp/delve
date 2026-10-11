---
title: Custom Git client dependency
type: value
id: '11.12'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s05_p02
- s05_p15
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Custom Git client dependency

Scaling features depend on a specialized Git client rather than only the standard Git distribution.

## Evidence

- **s05_p02** (accepts) · [[sources/s5|Introducing Scalar]]
  > What about Linux? There is potential for porting Scalar to Linux, so please comment on this issue if you would use Scalar on Linux. In the rest of this post, I’ll share three important lessons that informed Scalar’s design: Finally, I share our plan for contributing these features to the Git client. You can get started with Scalar using the …
- **s05_p15** (accepts) · [[sources/s5|Introducing Scalar]] · Scalar and the future of Git
  > - Scalar relies on a stable and correct filesystem watcher to scale growth in modified size, and Watchman does that decently well. However, Watchman is a much more general tool than we need, and it isn’t “Git aware.” It doesn’t know when a directory matches a \`.gitignore\` pattern and that we don’t need to scan it for changes. By creating …
