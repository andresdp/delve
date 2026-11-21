# Ticket routing as built

The help desk tool sends every new ticket to the routing service through a webhook. The service runs on a managed
Kubernetes cluster in the company's EU cloud region, with two replicas behind a load balancer. It first looks for
duplicates: if the same customer sent a ticket with the same subject in the last hour, the service attaches the
new ticket to the earlier one and does not classify it.

Otherwise the service turns the subject and the body into an embedding with a pretrained multilingual
sentence-embedding model, and a logistic-regression classifier with one class per team picks the team. The
service writes the team back to the help desk tool, with the two runner-up teams and the words that weighed most
in the decision, which the tool shows to agents next to the ticket.

When an agent moves a ticket, the help desk tool records the new team. Every Sunday a scheduled job exports the
tickets of the last 90 days with their final teams, retrains the classifier (the embedding model is never
retrained) and evaluates it on the last week's tickets. If it is at least as accurate as the current model, the
job replaces the model file in object storage, and the service loads the new file within five minutes.

A new team has no training data until agents move tickets to it. Until then, keyword rules written by the team's
lead route its tickets.

A dashboard shows, per team, the share of tickets that agents moved, and sends an alert when that share doubles
from one week to the next.
