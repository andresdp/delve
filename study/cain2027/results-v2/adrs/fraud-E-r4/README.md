# Architecture decisions: Card-fraud scoring service

* [serve scores synchronously for authorization](0001-serve-scores-synchronously-for-authorization.md)
* [persist and provide access to features](0002-persist-and-provide-access-to-features.md)
* [deploy model versions](0003-deploy-model-versions.md)
* [track inputs and outputs in production](0004-track-inputs-and-outputs-in-production.md)
* [version the data used for model development](0005-version-the-data-used-for-model-development.md)
* [test prediction service performance](0006-test-prediction-service-performance.md)

## Not grounded in the design space

* Exact latency objective and percentile, transaction volume, and peak-load profile.
* Availability target, failure behavior, and authorization fallback when scoring is unavailable.
* Audit retention period, required explanation format, and whether feature values or immutable references are sufficient.
* Model training, approval, and deployment controls; the design-space points checked had no attesting sources and are novel combinations.
