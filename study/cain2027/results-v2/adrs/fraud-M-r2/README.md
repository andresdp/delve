# Architecture decisions: Card-fraud scoring service

* [how should transaction scores be served](0001-how-should-transaction-scores-be-served.md)
* [what interface should the payment application use](0002-what-interface-should-the-payment-application-use.md)
* [how should inference features be stored and retrieved](0003-how-should-inference-features-be-stored-and-retrieved.md)
* [how should model versions and score lineage be recorded](0004-how-should-model-versions-and-score-lineage-be-recorded.md)
* [what should production monitoring cover](0005-what-should-production-monitoring-cover.md)

## Not grounded in the design space

* Fraud-score explanation format and per-transaction audit record schema.
* Availability target, fail-open or fail-closed behavior, and authorization timeout policy.
* Feature retention period, access controls, and audit retention requirements.
* Model choice, fraud-specific evaluation criteria, and promotion thresholds.
