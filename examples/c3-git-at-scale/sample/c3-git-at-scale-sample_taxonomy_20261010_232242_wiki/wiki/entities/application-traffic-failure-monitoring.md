---
title: Application-traffic failure monitoring
type: value
id: '11.11'
status: accepted
dimension: '[[concepts/repository-service-scaling|Repository Service Scaling]]'
accepted_by:
- s03_p03
- s03_p09
rejected_by: []
passages: 2
systems:
- '[[synthesis/systems/gh-spokes|GitHub Spokes]]'
tags:
- value
- accepted
- repository-service-scaling
---

# Application-traffic failure monitoring

Use failures observed during real authenticated repository requests, alongside heartbeats, to detect unhealthy servers.

## Evidence

- **s03_p03** (accepts) · [[sources/s3|Building resilience in Spokes]] · Availability
  > Spokes’s availability is a function of the availability of underlying servers and networks, and of our ability to detect and route around server and network problems. Individual servers become unavailable pretty frequently. Since rolling out Spokes this past spring, we have had individual servers crash due to a kernel deadlock and faulty RAM chips. Sometimes servers provide degraded service due …
- **s03_p09** (accepts) · [[sources/s3|Building resilience in Spokes]] · Clean shutdowns
  > So instead, we prepare a server for retirement by removing it from the count of active replicas for any repository. Spokes can still use that server for both read and write operations. But when it asks if all repositories have enough replicas, suddenly some of them—the ones on the retiring server—will say no, and more replicas will be created. These …
