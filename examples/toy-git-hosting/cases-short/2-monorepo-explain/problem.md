# Hosting an open-source monorepo

## Context

An open-source foundation hosts the monorepo of its largest project: 12 years of history, about 40 GB, about 300
pushes a day, and 2,000 contributors on five continents. Most clones come from CI services and from first-time
contributors, who need only the latest version. A volunteer team runs the service on donated servers in two data
centres, one in Europe and one in North America.

## Requirements

Functional:

- **R1.** Accept pushes from the maintainers to a single canonical repository over the standard Git protocol.
- **R2.** Let a first-time contributor start working without downloading the whole history.

Quality (as scenarios):

- **Q1 (performance).** A contributor in Asia or South America clones the latest version within two minutes on a
  50 Mbit/s connection.
- **Q2 (consistency).** A CI job that starts after a push has been accepted always fetches that push.

Constraints:

- **C1.** Four volunteers run the service in their spare time.
