# Architecture decisions: Card-fraud scoring service

* [how should transactions request fraud scores](0001-how-should-transactions-request-fraud-scores.md)
* [where should online prediction run](0002-where-should-online-prediction-run.md)
* [when should transaction predictions be computed](0003-when-should-transaction-predictions-be-computed.md)
* [how should features be stored for training and inference](0004-how-should-features-be-stored-for-training-and-inference.md)
* [how should model and feature changes be monitored](0005-how-should-model-and-feature-changes-be-monitored.md)
* [how should serving capacity respond to transaction peaks](0006-how-should-serving-capacity-respond-to-transaction-peaks.md)

## Not grounded in the design space

* Fraud-model family and decision threshold selection
* Authorization behavior when scoring or feature retrieval fails
* Audit retention period and access policy for transaction-level records
* Regional failover and recovery objectives
* Training labels, retraining cadence, and model promotion policy
