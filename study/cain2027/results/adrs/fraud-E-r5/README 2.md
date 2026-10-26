# Architecture decisions: Card-fraud scoring service

* [how to integrate the model](0001-how-to-integrate-the-model.md)
* [how to serve scores](0002-how-to-serve-scores.md)
* [how to persist and provide access to features](0003-how-to-persist-and-provide-access-to-features.md)
* [how to deploy model versions](0004-how-to-deploy-model-versions.md)
* [how to version training data](0005-how-to-version-training-data.md)
* [how to monitor and track production scoring](0006-how-to-monitor-and-track-production-scoring.md)
* [what to test in the scoring pipeline](0007-what-to-test-in-the-scoring-pipeline.md)

## Not grounded in the design space

* How to provide a highly available deployment across zones or regions.
* How to define the latency percentile and timeout/fallback behavior for authorization.
* How to protect cardholder data and control access to retained feature and score records.
* How to retain audit evidence and model artifacts for the required period.
