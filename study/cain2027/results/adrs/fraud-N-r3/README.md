# Architecture decisions: Card-fraud scoring service

* [Score transactions synchronously before authorization](0001-score-transactions-synchronously-before-authorization.md)
* [Scale stateless scoring workers horizontally](0002-scale-stateless-scoring-workers-horizontally.md)
* [Serve a pinned model version for each scoring request](0003-serve-a-pinned-model-version-for-each-scoring-request.md)
* [Record the model version and feature values with each score](0004-record-the-model-version-and-feature-values-with-each-score.md)

## Decisions left open

* Feature definitions, sources, and online freshness requirements.
* Training data, model development, validation, and deployment process.
* Availability targets and behavior when scoring or feature dependencies fail.
* Audit record retention, access controls, and storage technology.
* Traffic volumes, peak rates, and the precise latency objective.
