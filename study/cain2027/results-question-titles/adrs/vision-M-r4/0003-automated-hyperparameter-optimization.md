# Automated hyperparameter optimization

*How should weekly retraining be tuned?*

* System: On-device visual inspection

## Context and Problem Statement

The brief specifies weekly retraining from newly labelled images but gives no tuning process or need for rapid online updates. The team’s size and budget favor limiting repeated manual work.

## Decision Drivers

* Weekly retraining
* Small team
* Tight budget

## Considered Options

* Automated hyperparameter optimization (`v:28.4`)
* Manual hyperparameter tuning (`v:28.5`)
* Incremental online training (`v:28.3`)

## Decision Outcome

Chosen option: "Automated hyperparameter optimization" (`v:28.4`).

Automated tuning can reduce recurring manual search for a small team, while weekly batch retraining does not require online learning. The chosen point was novel but warning-free; the rival using incremental online training was likewise novel and warning-free.

### Consequences

* Bound the search to control compute.
* Validate each weekly candidate before release.
* Record tuning settings with model versions.

## Pros and Cons of the Options

### Automated hyperparameter optimization

* Good, because Reduces manual search
* Good, because Repeatable tuning
* Bad, because Search compute cost
* Bad, because Needs bounded search space
* Sources: `s02_p09`, `s04_p01`, `s09_p07`, `s17_p01`, `s17_p03`, `s17_p05`, `s17_p06`, `s18_p01`, `s18_p02`, `s18_p04`, `s19_p05`, `s22_p13`, `s24_p05`

### Manual hyperparameter tuning

* Good, because Direct team control
* Good, because No search service
* Bad, because Recurring staff effort
* Bad, because Slower iteration
* Sources: `s06_p07`, `s06_p11`

### Incremental online training

* Good, because Updates as data arrives
* Good, because Avoids full retraining
* Bad, because More complex operations
* Bad, because Not required by weekly cadence
* Sources: `s09_p03`, `s10_p09`, `s11_p01`, `s11_p02`, `s11_p06`, `s11_p09`, `s12_p02`, `s12_p04`, `s12_p05`, `s19_p06`, `s19_p08`, `s19_p16`, `s20_p02`, `s22_p09`
