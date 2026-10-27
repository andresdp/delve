# Architecture decisions: Retail demand forecasting

* [Orchestrated ML pipeline](0001-orchestrated-ml-pipeline.md)
* [Pipeline and experiment version control](0002-pipeline-and-experiment-version-control.md)
* [Commit-triggered staged release automation](0003-commit-triggered-staged-release-automation.md)
* [Threshold-based quality regression testing](0004-threshold-based-quality-regression-testing.md)
* [Traceable and preserved data](0005-traceable-and-preserved-data.md)

## Decisions left open

* Forecasting model family and seasonal or calendar feature strategy.
* Historical data storage and retrieval design, including retention duration.
* Forecast publication interface and consumer access patterns.
* Compute platform, deployment environment, and recovery objectives.
* Forecast quality metric definitions and acceptable thresholds.
