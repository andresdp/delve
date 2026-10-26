# Architecture decisions: Retail demand forecasting

* [how should weekly ml work be coordinated](0001-how-should-weekly-ml-work-be-coordinated.md)
* [how should past forecasts and training runs be reproduced](0002-how-should-past-forecasts-and-training-runs-be-reproduced.md)
* [how should forecasts be delivered](0003-how-should-forecasts-be-delivered.md)
* [how should code and model changes reach production](0004-how-should-code-and-model-changes-reach-production.md)
* [how should production forecasts be monitored](0005-how-should-production-forecasts-be-monitored.md)

## Not grounded in the design space

* Data ingestion mechanism and source-of-truth selection; the workflow coordination dimension explicitly requires this decision first.
* Forecast evaluation metrics, acceptance thresholds, and model promotion criteria.
* Historical raw data retention and point-in-time reconstruction policy for each past week.
* Forecast consumer interface, access control, and delivery format.
* Infrastructure and scheduling platform appropriate to the team's operational capacity.
