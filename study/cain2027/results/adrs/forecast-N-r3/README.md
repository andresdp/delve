# Architecture decisions: Retail demand forecasting

* [Version input data and pipeline code for reproducible historical forecasts](0001-version-input-data-and-pipeline-code-for-reproducible-histor.md)
* [Use a shared forecasting model across stores and products](0002-use-a-shared-forecasting-model-across-stores-and-products.md)
* [Run the forecast pipeline on a weekly schedule](0003-run-the-forecast-pipeline-on-a-weekly-schedule.md)
* [Promote model changes through a staged release](0004-promote-model-changes-through-a-staged-release.md)

## Decisions left open

* Source systems, data quality rules, and historical data availability.
* Forecast horizon and when forecasts must be delivered.
* Accuracy and business acceptance metrics.
* Runtime, storage, deployment, and monitoring platform.
* How forecasts are consumed and corrected after publication.
