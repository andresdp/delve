---
type: Design Alternative
title: Containerized chronological execution with a notebook-independent build process
description: Notebook workflows are containerized and chronologically stateful, while a separate build process or continuous-integration quality gate is used alongside the notebooks.
id: '45.3'
dimension: /concepts/notebook-execution-arrangement.md
accepted_by:
- s21_p07
- s29_p01
- s29_p02
- s29_p06
rejected_by:
- s26_p02
passages: 5
includes:
- Containerized notebook execution
- Chronological notebook state execution
- Notebook-independent build process
tags:
- value
- mixed
- notebook-execution-arrangement
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Containerized chronological execution with a notebook-independent build process

Notebook workflows are containerized and chronologically stateful, while a separate build process or continuous-integration quality gate is used alongside the notebooks.

## Evidence

- **s21_p07** (accepts) · [MLOps: What It Is, Why it Matters, and How To Implement It (from a Data Scientist Perspective)](/sources/s21.md)
- **s26_p02** (rejects) · [The Pros and Cons of Using Jupyter Notebooks as Your Editor for Data Science Work TL;DR: PyCharm's probably better](/sources/s26.md)
- **s29_p01** (accepts) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)
- **s29_p02** (accepts) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)
- **s29_p06** (accepts) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Containerized notebook execution**: Execution of notebook workflows in containers.
- **Chronological notebook state execution**: Relying on notebook cells progressing in scroll order to maintain computational state and narrative dependencies.
- **Notebook-independent build process**: Running notebooks without a separate build process or standard continuous-integration quality gate.
