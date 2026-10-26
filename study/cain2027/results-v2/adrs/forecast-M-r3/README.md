# Architecture decisions: Retail demand forecasting

* [Preserve data for historical replay](0001-preserve-data-for-historical-replay.md)
* [Version pipelines and experiments together](0002-version-pipelines-and-experiments-together.md)
* [Ingest weekly inputs in batches](0003-ingest-weekly-inputs-in-batches.md)
* [Coordinate recurring model runs](0004-coordinate-recurring-model-runs.md)
* [Promote model changes through staged automation](0005-promote-model-changes-through-staged-automation.md)
* [Evaluate candidates before promotion](0006-evaluate-candidates-before-promotion.md)
* [Develop model ideas iteratively](0007-develop-model-ideas-iteratively.md)

## Decisions left open

* How historical training labels and later corrections are versioned for past-week replay.
* The forecast quality metric and promotion threshold for weekly demand.
* How monitoring signals should combine and what action should follow drift or forecast degradation.
* How the weekly production run is isolated and recovered if a candidate or pipeline change fails.
