# Architecture decisions: Retail demand forecasting

* [Main requirements, in priority order](0001-main-requirements-in-priority-order.md)
* [Orchestrated ML pipeline](0002-orchestrated-ml-pipeline.md)
* [End-to-end reproducible lifecycle governance](0003-end-to-end-reproducible-lifecycle-governance.md)
* [Progressive release automation with rollback](0004-progressive-release-automation-with-rollback.md)
* [Offline evaluation pipeline](0005-offline-evaluation-pipeline.md)

## Decisions left open

* How to set forecast accuracy targets and business-specific evaluation metrics.
* How long to retain historical input data and run artifacts.
* How to monitor forecast quality and trigger retraining or rollback.
