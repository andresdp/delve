---
type: Reference
title: Relations between dimensions
tags:
- reference
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Relations between dimensions

A relation links two dimensions and reads left to right as one sentence: *source* — verb — *target*. In the graph view the arrow goes from the source to the target; *co-occurs with* has no direction and is drawn without an arrowhead.

| Type | Reads as (A = source, B = target) | Meaning | Example in this design space |
|---|---|---|---|
| *requires* | A requires B to be decided first | the source only applies once a choice has been made on the target | [ML Workflow Execution Coordination](/concepts/ml-workflow-execution-coordination.md) requires [Data Ingestion Mechanism](/concepts/data-ingestion-mechanism.md) to be decided first |
| *affects* | Choices on A affect the outcomes of B | choices on the source change the results, costs or risks seen on the target | Choices on [Data Ingestion Mechanism](/concepts/data-ingestion-mechanism.md) affect the outcomes of [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md) |
| *constrains* | Choices on A limit the options available on B | a choice on the source rules out or restricts some choices on the target | Choices on [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md) limit the options available on [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md) |
| *co occurs with* | A and B are usually decided together | the sources decide both together, but neither causes or requires the other | — |

## How they are made

- The model proposes relations while it builds and revises the design space, judged against the use case and the topics the sources discuss. Relations are **inferred**: unlike values, they are **not checked against passages**, and no passage is cited for them.
- Each relation is written as its sentence first; one whose sentence does not match its type and direction is rejected, as are opposite pairs (A requires B and B requires A), cycles of *requires* and relations beyond a small number per dimension.
- Runs made before these rules may contain relations in the wrong direction; they are shown as stored.
