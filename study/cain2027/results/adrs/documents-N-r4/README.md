# Architecture decisions: Large-scale document classification

* [Buffer incoming documents through a durable queue](0001-buffer-incoming-documents-through-a-durable-queue.md)
* [Scale LLM classification workers with queue demand](0002-scale-llm-classification-workers-with-queue-demand.md)
* [Publish classification results through a shared result store and interface](0003-publish-classification-results-through-a-shared-result-store.md)
* [Monitor classification quality over time](0004-monitor-classification-quality-over-time.md)

## Decisions left open

* Document ingestion formats and validation rules
* Whether and how uncertain classifications receive human review
* LLM provider, model selection, and fallback strategy
* Quality measurement method and source of ground-truth labels
* Retention, privacy, security, and regional data requirements
* Consumer latency and availability requirements
* Cost limits and per-document processing targets
