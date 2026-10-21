---
type: Overview
title: c3-git-at-scale-sample
run: '20261016_094637'
view: selected
dimensions: 8
values: 89
generation_llm: openai/gpt-5.6-luna
evaluation_llm: openai/gpt-5.6-luna
embedding: openai/text-embedding-3-small
tags:
- index
source_count: 5
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T09:46:37-03:00'
---

![ddspace](assets/ddspace-logo.svg)

# c3-git-at-scale-sample

This wiki presents a **design space** mined by ddspace from a corpus of documents. A design space organizes the architectural design decisions the documents discuss: each **dimension** is one decision a designer faces, and its **values** are the alternatives the documents describe. Every page is generated from the run's data, without rewording, and links to the evidence behind it. New to design spaces or to how they are mined? Start with [Approach](/approach.md).

Run 20261016_094637 (selected view): 8 dimensions, 89 values, 5 sources.

## Use case

*What the run was asked to find: the question that oriented the mining.*

Identify the architectural design decisions involved in making Git repositories work at scale, for very many repositories, very large repositories and very many users, on the hosting servers and on the clients, as documented in an engineering article and official engineering background material by the teams that built such systems. For each decision, identify the alternative options the teams adopted or considered and rejected, the forces (quality attributes, constraints and practical concerns) that drive the choice between them, and how decisions relate to one another. Each dimension must name one architectural design decision; its values are the alternative options for that decision.

## Dimensions

*A dimension is one design decision, phrased as a question a designer must answer. Its values are the alternative answers found in the sources, each with a status: **accepted** (adopted), **rejected** (considered and discarded), **mixed** (adopted by some sources, rejected by others) or **outcome** (an effect of decisions, not a choice).*

**Core dimensions** (8 of 8) have evidence from ≥ 2 sources, or supported by ≥ 2 systems: the axes the sources share. The others rest on a single source or system.

### Core

- ★ [Client Repository Performance Strategy](/concepts/client-repository-performance-strategy.md): 33 values
- ★ [Compaction Maintenance Technique](/concepts/compaction-maintenance-technique.md): 6 values
- ★ [Large-Repository Object Acquisition](/concepts/large-repository-object-acquisition.md): 9 values
- ★ [Replica State Comparison](/concepts/replica-state-comparison.md): 4 values
- ★ [Replica Synchronization Mechanism](/concepts/replica-synchronization-mechanism.md): 5 values
- ★ [Replica Topology](/concepts/replica-topology.md): 3 values
- ★ [Replica Write Coordination](/concepts/replica-write-coordination.md): 20 values
- ★ [Repository Placement and Read Routing](/concepts/repository-placement-and-read-routing.md): 9 values

## Synthesis

*Pages that look at the design space as a whole.*

- [Overview](/synthesis/overview.md): use case, run summary, narrative summary, and every dimension with its values by status
- [Contested decisions](/synthesis/contested.md): values some sources adopt and others reject
- [Dropped and unsupported](/synthesis/dropped.md): dimensions removed during selection, and values without evidence
- [System × dimension matrix](/synthesis/system-matrix.md): which value each system takes in each dimension
- [Design points](/synthesis/design-points.md): sampled combinations of values across dimensions
- [Evaluation](/synthesis/evaluation.md): how an LLM judge scored the design space, criterion by criterion

## Systems

*The concrete solutions the sources describe. A system's page shows the values its passages support, i.e. its position in the design space.*

- [Cursor Continuity and Origin](/synthesis/systems/cur-cont.md)
- [GitHub filesystem distribution](/synthesis/systems/gh-fs.md)
- [GitHub Spokes](/synthesis/systems/gh-spokes.md)
- [Google JGit on a DHT](/synthesis/systems/goog-dht.md)
- [Microsoft VFS for Git (GVFS)](/synthesis/systems/ms-gvfs.md)
- [Microsoft Scalar](/synthesis/systems/ms-scalar.md)

## Sources

*The documents the design space was mined from. A source's page lists the decisions it informs and whether it adopts or rejects each value.*

- [Git at any scale](/sources/s1.md): This technical article from Cursor describes the architecture of its Origin Git-hosting platform and Continuity storage system.
- [Stretching Spokes](/sources/s2.md): This is a technical architecture article about GitHub’s Spokes system for replicating Git repositories across geographically distant datacenters, including GitHub Enterprise.
- [Building resilience in Spokes](/sources/s3.md): This is a technical architecture document about GitHub’s Spokes replication system, formerly called DGit, which stores repositories, wikis, and gists.
- [Scalar philosophy](/sources/s4.md): This document describes Scalar, Microsoft’s Git performance configuration tool, and its relationship to custom Git builds and upstream Git features.
- [Introducing Scalar](/sources/s5.md): This technical announcement from Microsoft introduces Scalar, a .NET tool for improving Git performance in very large repositories.
