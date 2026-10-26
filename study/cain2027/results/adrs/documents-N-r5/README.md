# Architecture decisions: Large-scale document classification

* [Durable queue with workers](0001-durable-queue-with-workers.md)
* [Autoscaling worker pool](0002-autoscaling-worker-pool.md)
* [External hosted LLM API](0003-external-hosted-llm-api.md)
* [Versioned events per result](0004-versioned-events-per-result.md)
* [Validated structured output](0005-validated-structured-output.md)
* [Periodic labeled-sample evaluation](0006-periodic-labeled-sample-evaluation.md)

## Decisions left open

* Document format and preprocessing requirements
* Claim-type taxonomy ownership and change process
* Latency, availability, and recovery targets
* PII handling, data residency, and retention constraints
* Human review and escalation policy for uncertain classifications
* Provider selection, quotas, and cost limits
