# Architecture decisions: Retail demand forecasting

* [how should forecasts be reproducible for past weeks](0001-how-should-forecasts-be-reproducible-for-past-weeks.md)
* [how should model changes reach production](0002-how-should-model-changes-reach-production.md)
* [how should weekly forecasting be orchestrated](0003-how-should-weekly-forecasting-be-orchestrated.md)

## Not grounded in the design space

* Historical retention period and storage budget
* Input data sources, quality checks, and backfill policy
* Forecast accuracy targets and validation metrics
* Store and product scale, runtime limits, and forecast delivery interface
* Promotion authority, rollback policy, and production monitoring expectations
