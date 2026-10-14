---
title: No production traffic impact
type: value
id: '11.48'
status: outcome
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by: []
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
- '[[synthesis/systems/ms-scalar|Microsoft Scalar]]'
tags:
- value
- outcome
- repository-service-scaling
---

# No production traffic impact

The localized detector failure is exposed operationally without affecting production traffic.

## Evidence

- **s03_p05** (supports) · [[sources/s3|Building resilience in Spokes]] · Availability
  > The figure below illustrates the MxN nature of failure detection and shows in red which failure detectors are true if a single file server, \`dfs4\`, is offline. In one recent incident, a single front-end application server in a staging environment lost its ability to resolve the DNS names of the file servers. Because it couldn’t reach the file servers to …
- **s05_p04** (supports) · [[sources/s5|Introducing Scalar]] · Quick start for using the GVFS protocol
  > When using \`scalar clone\`, the working directory contains only the files at root using the Git sparse-checkout feature in \*cone mode\*. You can expand the files in your working directory using the \`git sparse-checkout set\` command, or fully populate your working directory by running \`git sparse-checkout disable\`. \`\`\` $ cd scalar/src $ ls AuthoringTests.md Directory.Build.targets SECURITY.md global.json CONTRIBUTING.md License.md Scalar.ruleset …
