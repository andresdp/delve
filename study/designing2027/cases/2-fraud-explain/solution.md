# Fraud scoring as built

The payments switch publishes every card transaction to a Kafka topic inside the PCI-certified environment.
Flink jobs consume the topic and keep per-card aggregates (spend and counts over the last hour, day and week, and
the number of distinct merchants) up to date in a Redis cluster. When a transaction arrives, the scoring service
reads the card's aggregates from Redis and adds the transaction's own fields.

The model is a gradient-boosted tree model (XGBoost). It is packaged in a container with a small Python REST
service and runs on the company's Kubernetes cluster, with six replicas and autoscaling on CPU. The
authorization switch calls the service synchronously with a 25 ms timeout. If the call times out or fails, the
switch uses the existing rule engine for that transaction and logs that no score was used. The service returns,
with every score, the three features that pushed the score up the most, which the dispute team uses to explain
declines to cardholders.

Every score is written, with the model version and all input values, to an append-only table in the company's
on-premises object store, kept for 13 months.

An Airflow pipeline retrains the model every night on the last 90 days of labelled transactions. MLflow records
the parameters, the metrics, the training data snapshot and the model artifact of every run, and holds the
model registry. A new model first runs in shadow mode next to the production model for three days; the risk team
reviews the comparison and promotes it by hand in MLflow. The scoring service loads the promoted model at its next
restart.

Grafana dashboards show the score distribution and the share of rule-engine fallbacks, and alert when the score
distribution drifts from last month's.
