# Architecture decisions: Retail demand forecasting

* [how to version data](0001-how-to-version-data.md)
* [should forecasting and training use batch or real time proce](0002-should-forecasting-and-training-use-batch-or-real-time-proce.md)
* [when and how to train the model](0003-when-and-how-to-train-the-model.md)
* [how to automate integration and delivery](0004-how-to-automate-integration-and-delivery.md)
* [what should automated testing cover](0005-what-should-automated-testing-cover.md)
* [how to monitor the model in production](0006-how-to-monitor-the-model-in-production.md)

## Not grounded in the design space

* Forecast quality metrics and acceptance thresholds.
* How model versions are promoted or rolled back safely.
* Storage and access design for forecasts by store and product.
* Operational ownership and response to failed weekly runs.
