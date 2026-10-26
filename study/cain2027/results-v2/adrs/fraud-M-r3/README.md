# Architecture decisions: Card-fraud scoring service

* [prediction serving mode](0001-prediction-serving-mode.md)
* [serving interface](0002-serving-interface.md)
* [feature serving storage](0003-feature-serving-storage.md)
* [ml lifecycle traceability](0004-ml-lifecycle-traceability.md)
* [peak serving capacity](0005-peak-serving-capacity.md)

## Not grounded in the design space

* Per-score audit record format, retention period, and access controls.
* Fraud-specific fallback behavior when features or model serving are unavailable.
* Feature-store consistency and synchronization guarantees.
