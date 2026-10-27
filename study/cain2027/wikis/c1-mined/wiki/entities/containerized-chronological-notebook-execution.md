---
type: Design Alternative
title: Containerized chronological notebook execution
description: Notebook workflows are containerized and depend on cells executing in chronological order to preserve computational state and narrative dependencies.
id: '45.2'
dimension: /concepts/notebook-execution-arrangement.md
accepted_by:
- s26_p01
- s27_p02
rejected_by:
- s26_p02
- s29_p01
- s29_p06
passages: 5
includes:
- Containerized notebook execution
- Chronological notebook state execution
tags:
- value
- mixed
- notebook-execution-arrangement
stance: mixed
generated:
  by: delvedspace/0.1.0.dev0
  at: '2026-10-16T23:36:51-03:00'
---

# Containerized chronological notebook execution

Notebook workflows are containerized and depend on cells executing in chronological order to preserve computational state and narrative dependencies.

## Evidence

- **s26_p01** (accepts) · [The Pros and Cons of Using Jupyter Notebooks as Your Editor for Data Science Work TL;DR: PyCharm's probably better](/sources/s26.md)
- **s26_p02** (rejects) · [The Pros and Cons of Using Jupyter Notebooks as Your Editor for Data Science Work TL;DR: PyCharm's probably better](/sources/s26.md)
- **s27_p02** (accepts) · [10 reasons why data scientists love Jupyter notebooks](/sources/s27.md)
- **s29_p01** (rejects) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)
- **s29_p06** (rejects) · [Jupyter Notebook is the Cancer of ML Engineering](/sources/s29.md)

## Includes

This alternative was defined from values the sources combine (value recoding); they are its facets:

- **Containerized notebook execution**: Execution of notebook workflows in containers.
- **Chronological notebook state execution**: Relying on notebook cells progressing in scroll order to maintain computational state and narrative dependencies.
