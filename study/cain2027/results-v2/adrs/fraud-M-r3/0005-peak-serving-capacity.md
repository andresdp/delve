# Peak serving capacity

* System: Card-fraud scoring service

## Context and Problem Statement

Transaction scoring must keep working through peaks without allowing model computation to miss its short deadline. Serving capacity therefore needs to respond to changing demand.

## Decision Drivers

* Availability: peak traffic
* Latency: tens of milliseconds

## Considered Options

* Elastic resource scaling (`v:26.6`)
* Scale-to-zero serving (`v:26.2`)
* Replicated mutable model instances (`v:26.4`)

## Decision Outcome

Chosen option: "Elastic resource scaling" (`v:26.6`).

Peak availability decides the choice: elastic scaling can add capacity with demand, while scale-to-zero risks startup delay against the latency deadline. We accept some unused warm capacity; “Productionizing Machine Learning with a Microservices Architecture” discusses scaling resources with workload demand.

### Consequences

* Set scaling limits and observe peak resource use.
* Keep sufficient warm capacity to protect the response deadline.

## Pros and Cons of the Options

### Elastic resource scaling

* Good, because Availability: scales compute with demand
* Good, because Latency: adds capacity during peaks
* Bad, because Availability: scaling may lag sudden demand changes
* Sources: `s02_p01`, `s04_p02`, `s04_p06`

### Scale-to-zero serving

* Good, because Cost: removes idle serving capacity
* Bad, because Latency: startup delay risks the scoring deadline
* Bad, because Availability: no warm capacity at low demand
* Sources: `s11_p04`, `s13_p09`

### Replicated mutable model instances

* Good, because Availability: serves from multiple instances
* Good, because Latency: distributes prediction load
* Bad, because Availability: mutable replicas require coordination
* Sources: `s12_p07`
