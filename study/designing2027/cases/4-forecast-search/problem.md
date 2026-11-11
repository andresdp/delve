# Retail demand forecasting

## Context

A retailer forecasts weekly demand per store and product: 400 stores and 30,000 products. Every Monday the
forecasts for the next eight weeks feed the replenishment system, which orders stock. Sales from the tills reach
the company's data warehouse every night; promotions and public holidays move demand strongly.

A team of three data scientists owns the forecasting pipeline end to end. The data warehouse is run by the
central IT department, which the team cannot change.

## Requirements

Functional:

- **R1.** Produce, every week, the forecast per store and product for the next eight weeks, and deliver it to the
  replenishment system by Monday 06:00.
- **R2.** Run the forecast again for any past week exactly as it was produced.
- **R3.** Try new model ideas and compare them with the production model on past weeks before they replace it.

Quality (as scenarios):

- **Q1 (reproducibility).** Asked for the forecast of a week up to two years back, the team produces the same
  numbers within one working day.
- **Q2 (development velocity).** A new model idea that beats the production model on past weeks reaches
  production within one week, with no manual step except the approval.
- **Q3 (reliability).** When a weekly run fails, the team is told within 15 minutes, and the replenishment system
  never receives a partial forecast.
- **Q4 (maintainability).** A new team member can run the whole pipeline on their own machine within their first
  week.

Constraints:

- **C1.** Three data scientists, with no data engineers; the data warehouse stays as it is.
- **C2.** The weekly run must fit in the six hours between the nightly load and the Monday deadline.
