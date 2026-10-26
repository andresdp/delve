# Architecture decisions: Retail demand forecasting

* [Versioned inputs and model artifacts](0001-versioned-inputs-and-model-artifacts.md)
* [Validate candidates, then promote explicitly](0002-validate-candidates-then-promote-explicitly.md)
* [Scheduled batch pipeline](0003-scheduled-batch-pipeline.md)

## Decisions left open

* Historical retention period and storage budget
* Input data sources, quality checks, and backfill policy
* Forecast accuracy targets and validation metrics
* Store and product scale, runtime limits, and forecast delivery interface
* Promotion authority, rollback policy, and production monitoring expectations
