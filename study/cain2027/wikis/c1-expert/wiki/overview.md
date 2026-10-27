---
type: Overview
title: c1-e
run: '20261026_115406'
view: selected
dimensions: 28
values: 124
generation_llm: openai/gpt-5.6-luna
evaluation_llm: openai/gpt-5.6-luna
embedding: openai/text-embedding-3-small
tags:
- index
source_count: 0
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-26T11:54:06-03:00'
---

![ddspace](assets/ddspace-logo.svg)

# c1-e

This wiki presents a **design space** mined by ddspace from a corpus of documents. A design space organizes the architectural design decisions the documents discuss: each **dimension** is one decision a designer faces, and its **values** are the alternatives the documents describe. Every page is generated from the run's data, without rewording, and links to the evidence behind it. New to design spaces or to how they are mined? Start with [Approach](/approach.md).

Run 20261026_115406 (selected view): 28 dimensions, 124 values, 0 sources.

## Use case

*What the run was asked to find: the question that oriented the mining.*

Identify the architectural design decisions that practitioners face when designing and implementing machine learning systems along the machine learning workflow — from data ingestion and processing, through model building and training, to putting models into production and operating them — as documented in practitioner (gray) literature. For each decision, identify the alternative decision options practitioners use or consider, the forces (quality attributes, constraints and practical concerns) that drive the choice between them, and how decisions relate to one another. Each dimension must name one architectural design decision; its values are the alternative options for that decision.

## Dimensions

*A dimension is one design decision, phrased as a question a designer must answer. Its values are the alternative answers found in the sources, each with a status: **accepted** (adopted), **rejected** (considered and discarded), **mixed** (adopted by some sources, rejected by others) or **outcome** (an effect of decisions, not a choice).*

**Core dimensions** (28 of 28) have evidence from ≥ 0 sources: the axes the sources share. The others rest on a single source or system.

### Core

- ★ [How to adjust models based on monitoring results?](/concepts/how-to-adjust-models-based-on-monitoring-results.md): 2 values
- ★ [How to automatically process the data used for model building?](/concepts/how-to-automatically-process-the-data-used-for-model-building.md): 4 values
- ★ [How to automatically provision environments?](/concepts/how-to-automatically-provision-environments.md): 2 values
- ★ [How to design the interface for data access?](/concepts/how-to-design-the-interface-for-data-access.md): 5 values
- ★ [How to inform clients about prediction result availability?](/concepts/how-to-inform-clients-about-prediction-result-availability.md): 3 values
- ★ [How to ingest data into ML projects or applications?](/concepts/how-to-ingest-data-into-ml-projects-or-applications.md): 4 values
- ★ [How to integrate a machine learning model in an application?](/concepts/how-to-integrate-a-machine-learning-model-in-an-application.md): 7 values
- ★ [How to monitor and track the model in production?](/concepts/how-to-monitor-and-track-the-model-in-production.md): 4 values
- ★ [How to parallelize data processing?](/concepts/how-to-parallelize-data-processing.md): 4 values
- ★ [How to parallelize model building?](/concepts/how-to-parallelize-model-building.md): 5 values
- ★ [How to perform automatic integration and delivery in a machine learning context?](/concepts/how-to-perform-automatic-integration-and-delivery-in-a-machine-learning-context.md): 4 values
- ★ [How to perform model building in an ML project?](/concepts/how-to-perform-model-building-in-an-ml-project.md): 3 values
- ★ [How to persist and provide access to features?](/concepts/how-to-persist-and-provide-access-to-features.md): 2 values
- ★ [How to serve model predictions or scores?](/concepts/how-to-serve-model-predictions-or-scores.md): 5 values
- ★ [How to store data used in machine learning applications?](/concepts/how-to-store-data-used-in-machine-learning-applications.md): 4 values
- ★ [How to trigger a machine learning pipeline or orchestrator?](/concepts/how-to-trigger-a-machine-learning-pipeline-or-orchestrator.md): 6 values
- ★ [How to version data decision?](/concepts/how-to-version-data-decision.md): 3 values
- ★ [Should AutoML be used and if so where?](/concepts/should-automl-be-used-and-if-so-where.md): 2 values
- ★ [Should MLOps be used and if so when?](/concepts/should-mlops-be-used-and-if-so-when.md): 2 values
- ★ [Should data be processed in batches or in realtime?](/concepts/should-data-be-processed-in-batches-or-in-realtime.md): 2 values
- ★ [What development environment should be used?](/concepts/what-development-environment-should-be-used.md): 2 values
- ★ [What to build, test, and deploy automatically by CI/CD pipelines?](/concepts/what-to-build-test-and-deploy-automatically-by-ci-cd-pipelines.md): 3 values
- ★ [What to test in a machine learning/data science pipeline?](/concepts/what-to-test-in-a-machine-learning-data-science-pipeline.md): 14 values
- ★ [When and how to train the model?](/concepts/when-and-how-to-train-the-model.md): 3 values
- ★ [Which data processing tasks can be performed by a data processing pipeline or component?](/concepts/which-data-processing-tasks-can-be-performed-by-a-data-processing-pipeline-or-co.md): 7 values
- ★ [Which model versions should be deployed to production and how?](/concepts/which-model-versions-should-be-deployed-to-production-and-how.md): 3 values
- ★ [Which tasks can be performed by a delivery pipeline or component?](/concepts/which-tasks-can-be-performed-by-a-delivery-pipeline-or-component.md): 9 values
- ★ [Which tasks can be performed by a model building pipeline or component?](/concepts/which-tasks-can-be-performed-by-a-model-building-pipeline-or-component.md): 10 values

## Synthesis

*Pages that look at the design space as a whole.*

- [Overview](/synthesis/overview.md): use case, run summary, narrative summary, and every dimension with its values by status
- [Contested decisions](/synthesis/contested.md): values some sources adopt and others reject
- [Dropped and unsupported](/synthesis/dropped.md): dimensions removed during selection, and values without evidence

## Sources

*The documents the design space was mined from. A source's page lists the decisions it informs and whether it adopts or rejects each value.*
