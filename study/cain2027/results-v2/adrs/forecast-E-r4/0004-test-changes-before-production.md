# Test changes before production

* System: Retail demand forecasting

## Context and Problem Statement

New model ideas must reach production without breaking the weekly forecast. The design space lists testing options, but provides no evidence passages or system attestations.

## Decision Drivers

* 1. Protect weekly run
* 2. Fast model iteration
* 3. Small team

## Considered Options

* Testing trained model quality (`v:26.9`)
* System integration testing (`v:26.5`)
* Canary testing (`v:26.1`)

## Decision Outcome

Chosen option: "Testing trained model quality" (`v:26.9`).

Protecting the weekly run decides the choice: check trained model quality before release. This requires the team to define acceptance criteria, and by itself does not validate pipeline integration or rollout behavior.

### Consequences

* Set an explicit quality gate for candidate models.
* Add integration or rollout checks if the weekly run requires them; the brief does not specify their form.

## Pros and Cons of the Options

### Testing trained model quality

* Good, because Protect weekly run: checks model quality before release
* Bad, because Small team: requires a defined quality criterion
* Sources: `d:26`, `v:26.9`

### System integration testing

* Good, because Protect weekly run: exercises connected components
* Bad, because Fast iteration: adds integration setup and runtime
* Sources: `d:26`, `v:26.5`

### Canary testing

* Good, because Protect weekly run: limits initial exposure
* Bad, because Small team: requires rollout and observation support
* Sources: `d:26`, `v:26.1`
