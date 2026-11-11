# Git hosting for a fast-growing engineering organization

## Context

A software company hosts its own Git service. It has 3,000 engineers in four regions, and its CI system starts
about 40,000 jobs a day, each of which fetches the repository it builds. The largest repository holds 15 years of
history (about 200 GB) and most engineers touch only a small part of it. The service runs in the company's cloud
account; a team of five engineers builds and operates it.

## Requirements

Functional:

- **R1.** Accept pushes and serve fetches and clones for every repository over the standard Git protocol.
- **R2.** Let engineers work on the largest repository without downloading all of it.

Quality (as scenarios):

- **Q1 (durability).** When any single machine or disk is lost, no pushed commit is lost.
- **Q2 (availability).** When one server fails during working hours, pushes and fetches continue within one
  minute, without an operator.
- **Q3 (performance).** A CI job in any region fetches the latest state of a repository within 30 seconds at the
  95th percentile, even right after a push.
- **Q4 (consistency).** A fetch that starts after a push has succeeded always sees that push.

Constraints:

- **C1.** Five engineers build and run the service.
- **C2.** Engineers keep using standard Git clients; no custom client may be required.
