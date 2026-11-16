# Support-ticket routing

## Context

A software company receives about 20,000 support tickets a day, in English, Spanish and Portuguese, by e-mail and
through a web form. Each ticket must reach one of 25 support teams. Today a first-line team reads every ticket and
forwards it by hand, and a ticket sent to the wrong team waits a day on average before it reaches the right one.
Products, and the teams that support them, change a few times a year.

## Requirements

Functional:

- **R1.** Assign every new ticket to a team, and let a support agent move it to another team when the assignment
  is wrong.
- **R2.** Learn from the moves that support agents make.

Quality (as scenarios):

- **Q1 (latency).** At the daily peak of 3,000 tickets an hour, a ticket is assigned within 10 seconds of its
  arrival.
- **Q2 (adaptability).** When a new team is created for a new product, at least 80% of the tickets meant for it
  reach it within two weeks.

Constraints:

- **C1.** Tickets may contain customers' personal data and must not leave the company's cloud region in the EU.
