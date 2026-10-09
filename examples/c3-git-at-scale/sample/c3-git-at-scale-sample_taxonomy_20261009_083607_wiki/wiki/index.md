---
title: c3-git-at-scale-sample
type: index
run: '20261009_083607'
view: selected
dimensions: 5
values: 177
sources: 5
generation_llm: openai/gpt-5.6-luna
evaluation_llm: openai/gpt-5.6-luna
embedding: openai/text-embedding-3-small
tags:
- index
---

![DelveDSpace](assets/delvedspace-logo.svg)

# c3-git-at-scale-sample

This wiki presents a **design space** mined by DelveDSpace from a corpus of documents. A design space organizes the architectural design decisions the documents discuss: each **dimension** is one decision a designer faces, and its **values** are the alternatives the documents describe. Every page is generated from the run's data, without rewording, and links to the evidence behind it. New to design spaces or to how they are mined? Start with [[approach|Approach]].

Run 20261009_083607 (selected view): 5 dimensions, 177 values, 5 sources.

## Use case

*What the run was asked to find: the question that oriented the mining.*

Identify the architectural design decisions involved in making Git repositories work at scale, for very many repositories, very large repositories and very many users, on the hosting servers and on the clients, as documented in an engineering article and official engineering background material by the teams that built such systems. For each decision, identify the alternative options the teams adopted or considered and rejected, the forces (quality attributes, constraints and practical concerns) that drive the choice between them, and how decisions relate to one another. Each dimension must name one architectural design decision; its values are the alternative options for that decision.

## Dimensions

*A dimension is one design decision, phrased as a question a designer must answer. Its values are the alternative answers found in the sources, each with a status: **accepted** (adopted), **rejected** (considered and discarded), **mixed** (adopted by some sources, rejected by others) or **outcome** (an effect of decisions, not a choice).*

**Core dimensions** (5 of 5) have evidence from ≥ 2 sources, or supported by ≥ 2 systems: the axes the sources share. The others rest on a single source or system.

### Core

- ★ [[concepts/client-repository-workload-scaling|Client Repository Workload Scaling]]: 38 values
- ★ [[concepts/git-hosting-and-acceleration-integration|Git Hosting and Acceleration Integration]]: 42 values
- ★ [[concepts/replica-failure-repair-and-failover|Replica Failure Repair and Failover]]: 36 values
- ★ [[concepts/repository-replica-placement|Repository Replica Placement]]: 20 values
- ★ [[concepts/write-coordination-and-replica-consistency|Write Coordination and Replica Consistency]]: 41 values

## Synthesis

*Pages that look at the design space as a whole.*

- [[synthesis/overview|Overview]]: use case, run summary, narrative summary, and every dimension with its values by status
- [[synthesis/contested|Contested decisions]]: values some sources adopt and others reject
- [[synthesis/dropped|Dropped and unsupported]]: dimensions removed during selection, and values without evidence
- [[synthesis/system-matrix|System × dimension matrix]]: which value each system takes in each dimension
- [[synthesis/design-points|Design points]]: sampled combinations of values across dimensions
- [[synthesis/evaluation|Evaluation]]: how an LLM judge scored the design space, criterion by criterion

## Systems

*The concrete solutions the sources describe. A system's page shows the values its passages support, i.e. its position in the design space.*

- [[synthesis/systems/cur-cont|Cursor Continuity and Origin]]
- [[synthesis/systems/gh-fs|GitHub filesystem distribution]]
- [[synthesis/systems/gh-spokes|GitHub Spokes]]
- [[synthesis/systems/goog-dht|Google JGit on a DHT]]
- [[synthesis/systems/ms-gvfs|Microsoft VFS for Git (GVFS)]]
- [[synthesis/systems/ms-scalar|Microsoft Scalar]]

## Sources

*The documents the design space was mined from. A source's page lists the decisions it informs and whether it adopts or rejects each value.*

- [[sources/s1|Git at any scale]]: This technical article from Cursor describes the architecture of its Origin Git-hosting platform and Continuity storage system.
- [[sources/s2|Stretching Spokes]]: This is a technical architecture article about GitHub’s Spokes system for replicating Git repositories across geographically distant datacenters, including GitHub Enterprise.
- [[sources/s3|Building resilience in Spokes]]: This is a technical architecture document about GitHub’s Spokes replication system, formerly called DGit, which stores repositories, wikis, and gists.
- [[sources/s4|Scalar philosophy]]: This document describes Scalar, Microsoft’s Git performance configuration tool, and its relationship to custom Git builds and upstream Git features.
- [[sources/s5|Introducing Scalar]]: This technical announcement from Microsoft introduces Scalar, a .NET tool for improving Git performance in very large repositories.
