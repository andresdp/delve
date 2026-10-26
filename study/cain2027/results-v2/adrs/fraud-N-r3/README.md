# Architecture decisions: Card-fraud scoring service

* [how should transaction scores be served](0001-how-should-transaction-scores-be-served.md)
* [how should the service handle peaks and failures](0002-how-should-the-service-handle-peaks-and-failures.md)
* [how should each score be made auditable](0003-how-should-each-score-be-made-auditable.md)
* [how should model versions be released](0004-how-should-model-versions-be-released.md)

## Not grounded in the design space

* Feature generation and source-of-truth design
* Feature freshness and missing-data behavior
* Model training, validation, and approval process
* Audit record retention duration and privacy constraints
* Capacity targets, failure objectives, and overload behavior
* Score thresholding and authorization policy
