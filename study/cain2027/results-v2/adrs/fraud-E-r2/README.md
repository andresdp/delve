# Architecture decisions: Card-fraud scoring service

* [how should transaction scoring be integrated](0001-how-should-transaction-scoring-be-integrated.md)
* [how should online predictions be served](0002-how-should-online-predictions-be-served.md)
* [should transaction features be processed in batch or in real](0003-should-transaction-features-be-processed-in-batch-or-in-real.md)
* [how should features be persisted and accessed](0004-how-should-features-be-persisted-and-accessed.md)
* [how should data used for model building be versioned](0005-how-should-data-used-for-model-building-be-versioned.md)
* [how should production model versions be deployed](0006-how-should-production-model-versions-be-deployed.md)
* [what production model information should be monitored and tr](0007-what-production-model-information-should-be-monitored-and-tr.md)

## Not grounded in the design space

* How to meet the tens-of-milliseconds latency target with a concrete latency budget and timeout policy.
* How to achieve availability targets, including redundancy, failover, and behavior when scoring is unavailable.
* How scores, model versions, and feature inputs are durably linked and retained for auditors.
* How to validate score quality and approve model releases; the design space offers test categories (d:26) but the brief does not specify acceptance criteria.
