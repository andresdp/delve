# Architecture decisions: Card-fraud scoring service

* [Use synchronous online scoring before transaction authorization](0001-use-synchronous-online-scoring-before-transaction-authorizat.md)
* [Serve the scoring model in a horizontally scalable stateless tier](0002-serve-the-scoring-model-in-a-horizontally-scalable-stateless.md)
* [Version models as immutable deployable artifacts](0003-version-models-as-immutable-deployable-artifacts.md)
* [Record the model version and feature snapshot for every score](0004-record-the-model-version-and-feature-snapshot-for-every-scor.md)

## Decisions left open

* Feature definitions, sources, and online freshness requirements
* Model training, validation, approval, and deployment process
* Authorization behavior on scoring timeout or service failure
* Audit retention period and required explanation format
* Security, privacy, and regulatory constraints for transaction features
