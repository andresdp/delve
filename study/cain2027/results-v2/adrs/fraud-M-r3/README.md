# Architecture decisions: Card-fraud scoring service

* [Prediction serving mode](0001-prediction-serving-mode.md)
* [Serving interface](0002-serving-interface.md)
* [Feature serving storage](0003-feature-serving-storage.md)
* [ML lifecycle traceability](0004-ml-lifecycle-traceability.md)
* [Peak serving capacity](0005-peak-serving-capacity.md)

## Decisions left open

* Per-score audit record format, retention period, and access controls.
* Fraud-specific fallback behavior when features or model serving are unavailable.
* Feature-store consistency and synchronization guarantees.
