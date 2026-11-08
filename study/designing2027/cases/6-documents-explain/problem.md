# Large-scale document classification

## Context

An insurer receives between two and eight million documents a day (scanned forms, e-mails, PDFs) and classifies
each one into one of 60 claim types with an LLM-based classifier. Volume varies strongly over the year: storm
season brings four times the usual load. Three teams use the results: claims handling, fraud investigation and
analytics. The documents contain personal data.

## Requirements

Functional:

- **R1.** Classify every incoming document into a claim type, with a confidence.
- **R2.** Deliver the results to the three consuming teams.
- **R3.** Send the documents the classifier is unsure about to human review, and use the reviewers' corrections
  to improve the classifier.

Quality (as scenarios):

- **Q1 (throughput and scalability).** During storm season, at eight million documents a day, every document is
  classified within two hours of arrival.
- **Q2 (observability).** When classification quality drops for one claim type (for example, after a form
  changes its layout), operators see it within one day.
- **Q3 (cost).** The classification costs less than 0.2 cents per document on average over the year.
- **Q4 (loose coupling).** A consuming team can change how it processes the results without the other teams or
  the classifier having to change.

Constraints:

- **C1.** The documents contain personal data and may not leave the EU.
- **C2.** The classifier uses an LLM from the insurer's approved provider, in its EU region.
