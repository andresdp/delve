# Architecture decisions: Card-fraud scoring service

* [Serve scores synchronously for authorization](0001-serve-scores-synchronously-for-authorization.md)
* [Persist and provide access to features](0002-persist-and-provide-access-to-features.md)
* [Deploy model versions](0003-deploy-model-versions.md)
* [Track inputs and outputs in production](0004-track-inputs-and-outputs-in-production.md)
* [Version the data used for model development](0005-version-the-data-used-for-model-development.md)
* [Test prediction service performance](0006-test-prediction-service-performance.md)

## Decisions left open

* Exact latency objective and percentile, transaction volume, and peak-load profile.
* Availability target, failure behavior, and authorization fallback when scoring is unavailable.
* Audit retention period, required explanation format, and whether feature values or immutable references are sufficient.
* Model training, approval, and deployment controls; the design-space points checked had no attesting sources and are novel combinations.
