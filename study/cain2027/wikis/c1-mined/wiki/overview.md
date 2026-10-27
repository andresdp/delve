---
type: Overview
title: c1-m
run: '20261016_233651'
view: selected
dimensions: 32
values: 279
generation_llm: openai/gpt-5.6-luna
evaluation_llm: openai/gpt-5.6-luna
embedding: openai/text-embedding-3-small
tags:
- index
source_count: 28
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

![ddspace](assets/ddspace-logo.svg)

# c1-m

This wiki presents a **design space** mined by ddspace from a corpus of documents. A design space organizes the architectural design decisions the documents discuss: each **dimension** is one decision a designer faces, and its **values** are the alternatives the documents describe. Every page is generated from the run's data, without rewording, and links to the evidence behind it. New to design spaces or to how they are mined? Start with [Approach](/approach.md).

Run 20261016_233651 (selected view): 32 dimensions, 279 values, 28 sources.

## Use case

*What the run was asked to find: the question that oriented the mining.*

Identify the architectural design decisions that practitioners face when designing and implementing machine learning systems along the machine learning workflow — from data ingestion and processing, through model building and training, to putting models into production and operating them — as documented in practitioner (gray) literature. For each decision, identify the alternative decision options practitioners use or consider, the forces (quality attributes, constraints and practical concerns) that drive the choice between them, and how decisions relate to one another. Each dimension must name one architectural design decision; its values are the alternative options for that decision.

## Dimensions

*A dimension is one design decision, phrased as a question a designer must answer. Its values are the alternative answers found in the sources, each with a status: **accepted** (adopted), **rejected** (considered and discarded), **mixed** (adopted by some sources, rejected by others) or **outcome** (an effect of decisions, not a choice).*

**Core dimensions** (23 of 32) have evidence from ≥ 9 sources: the axes the sources share. The others rest on a single source or system.

### Core

- ★ [Dataset Access and Availability](/concepts/dataset-access-and-availability.md): 6 values
- ★ [ML Artifact and Lifecycle Versioning](/concepts/ml-artifact-and-lifecycle-versioning.md): 7 values
- ★ [ML Code and Asset Organization](/concepts/ml-code-and-asset-organization.md): 13 values
- ★ [ML Data Governance and Preservation](/concepts/ml-data-governance-and-preservation.md): 6 values
- ★ [ML Data Transformation and Feature Engineering](/concepts/ml-data-transformation-and-feature-engineering.md): 6 values
- ★ [ML Feature and Data Serving Storage](/concepts/ml-feature-and-data-serving-storage.md): 5 values
- ★ [ML Integration Testing Strategy](/concepts/ml-integration-testing-strategy.md): 9 values
- ★ [ML Interactive Development Environment](/concepts/ml-interactive-development-environment.md): 3 values
- ★ [ML Organizational and Process Approach](/concepts/ml-organizational-and-process-approach.md): 9 values
- ★ [ML Release Automation](/concepts/ml-release-automation.md): 5 values
- ★ [ML Workflow Execution Coordination](/concepts/ml-workflow-execution-coordination.md): 3 values
- ★ [ML Workflow Infrastructure Strategy](/concepts/ml-workflow-infrastructure-strategy.md): 3 values
- ★ [MLOps Automation and Composition](/concepts/mlops-automation-and-composition.md): 10 values
- ★ [Model Evaluation and Regression Strategy](/concepts/model-evaluation-and-regression-strategy.md): 15 values
- ★ [Model Family and Combination Strategy](/concepts/model-family-and-combination-strategy.md): 5 values
- ★ [Model Learning, Tuning, and Update Strategy](/concepts/model-learning-tuning-and-update-strategy.md): 11 values
- ★ [Model Packaging and Runtime Placement](/concepts/model-packaging-and-runtime-placement.md): 28 values
- ★ [Model Serving Interface](/concepts/model-serving-interface.md): 8 values
- ★ [Prediction Serving Mode and Performance](/concepts/prediction-serving-mode-and-performance.md): 17 values
- ★ [Production Monitoring and Adaptation](/concepts/production-monitoring-and-adaptation.md): 30 values
- ★ [Runtime Resource and Performance Strategy](/concepts/runtime-resource-and-performance-strategy.md): 17 values
- ★ [Runtime State and Communication Strategy](/concepts/runtime-state-and-communication-strategy.md): 6 values
- ★ [Training Execution and Scaling Strategy](/concepts/training-execution-and-scaling-strategy.md): 6 values

### Other

- [Data Ingestion Mechanism](/concepts/data-ingestion-mechanism.md): 11 values
- [Data Labeling Strategy](/concepts/data-labeling-strategy.md): 2 values
- [ML Delivery and Problem Framing](/concepts/ml-delivery-and-problem-framing.md): 4 values
- [ML Dependency and Service Structure](/concepts/ml-dependency-and-service-structure.md): 4 values
- [ML Technology Selection Governance](/concepts/ml-technology-selection-governance.md): 7 values
- [ML Workflow Execution Mode](/concepts/ml-workflow-execution-mode.md): 3 values
- [MLOps Platform Ownership and Sourcing](/concepts/mlops-platform-ownership-and-sourcing.md): 7 values
- [Neural Architecture Search Strategy](/concepts/neural-architecture-search-strategy.md): 9 values
- [Notebook Execution Arrangement](/concepts/notebook-execution-arrangement.md): 4 values

## Synthesis

*Pages that look at the design space as a whole.*

- [Overview](/synthesis/overview.md): use case, run summary, narrative summary, and every dimension with its values by status
- [Contested decisions](/synthesis/contested.md): values some sources adopt and others reject
- [Dropped and unsupported](/synthesis/dropped.md): dimensions removed during selection, and values without evidence

## Sources

*The documents the design space was mined from. A source's page lists the decisions it informs and whether it adopts or rejects each value.*

- [How to power up your product by machine learning with python microservice, pt. 1](/sources/s1.md)
- [Architecting a Machine Learning Pipeline: How to build scalable Machine Learning systems - Part 2/2](/sources/s2.md)
- [Some Thoughts on Modularization in Machine Learning](/sources/s3.md)
- [Productionizing Machine Learning with a Microservices Architecture](/sources/s4.md)
- [Microservices Suck for Machine Learning (and what we did about it)](/sources/s5.md)
- [MLOps: Continuous delivery and automation pipelines in machine learning](/sources/s6.md)
- [Composing Deep-Learning Microservices for the Hybrid Internet of Things](/sources/s7.md)
- [Continuous Intelligence: Moving Machine Learning Application into Production Reliably](/sources/s8.md)
- [Architecture of a real-world Machine Learning system](/sources/s9.md)
- [Architecting a Machine Learning System for Risk](/sources/s10.md)
- [Architecting a Scalable Real Time Learning System](/sources/s11.md)
- [System Architectures for Personalization and Recommendation](/sources/s12.md)
- [Architectural thinking in the Wild West of data science](/sources/s13.md)
- [Scalable Software and Big Data Architecture - Big Data and Analytics Architectural Patterns](/sources/s15.md)
- [Machine Learning in Production: Software Architecture](/sources/s16.md)
- [AutoML](/sources/s17.md)
- [AutoML is Overhyped](/sources/s18.md)
- [Three Levels of ML Software](/sources/s19.md)
- [MLOps: Methods and Tools of DevOps for Machine Learning](/sources/s20.md)
- [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- [MLOps Principles](/sources/s22.md)
- [Machine Learning Monitoring: What It Is, and What We Are Missing](/sources/s23.md)
- [Automated monitoring of your machine learning models with Amazon SageMaker Model Monitor and sending predictions to human review workflows using Amazon A2I](/sources/s24.md)
- [MLOps: Model management, deployment, and monitoring with Azure Machine Learning](/sources/s25.md)
- [The Pros and Cons of Using Jupyter Notebooks as Your Editor for Data Science Work TL;DR: PyCharm's probably better](/sources/s26.md)
- [10 reasons why data scientists love Jupyter notebooks](/sources/s27.md)
- [5 reasons why jupyter notebooks suck](/sources/s28.md)
- [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)
