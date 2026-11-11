# Card-fraud scoring service

## Context

A payments company scores every card transaction for fraud before it is authorized. It processes about 3,000
transactions per second on a normal day and up to five times as many during seasonal sales. Fraudsters adapt
within weeks, and the confirmed fraud labels (chargebacks) arrive days to weeks after the transaction. Auditors
and the card schemes can ask, months later, why a given transaction was scored the way it was.

The ML team has five data scientists and two ML engineers. The company's operations team runs the data centres
and the shared infrastructure, but there is no platform team for machine learning.

## Requirements

Functional:

- **R1.** Score every card transaction before the authorization decision, using the cardholder's recent
  activity (for example, the spending of the last hour and the last day).
- **R2.** Update the model as new confirmed fraud cases arrive.
- **R3.** For any past score, show which model version and which input values produced it.

Quality (as scenarios):

- **Q1 (latency).** During a seasonal peak of 15,000 transactions per second, a score comes back within 30 ms at
  the 99th percentile.
- **Q2 (availability).** When the scoring service or one of its data sources fails, authorizations go on. The
  business accepts weaker fraud detection for up to 15 minutes, but no authorization may fail because of
  scoring.
- **Q3 (auditability).** An auditor asks about a score from up to 13 months ago. Within one working day the team
  answers with the model version, the input values and the training data that model was built from.
- **Q4 (adaptability).** When the fraud loss rate rises in one segment, a retrained model can be in production
  within 48 hours, after it has been compared with the current model on recent transactions.

Constraints:

- **C1.** Card data must stay inside the company's PCI-certified environment: no external service may process
  it.
- **C2.** Seven people build and run the system, with no dedicated ML platform team.
