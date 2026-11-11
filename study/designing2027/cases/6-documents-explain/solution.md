# Document classification as built

Incoming documents land in an object storage bucket in the EU region, and each upload puts a message on a Kafka
topic. A preprocessing service reads the topic, extracts the text (with OCR for scanned forms), removes duplicates
by content hash and writes the text next to the document.

A classifier service, running on Kubernetes, sends the text to the approved provider's LLM in its EU region. The
prompt lists the 60 claim types with a short definition and ten labelled examples, and asks for a claim type and
a confidence between 0 and 1. Small documents are sent in batches of 20 to reduce cost. The number of classifier
workers scales with the length of the Kafka topic's backlog, from 4 to 120. Every result is stored with the
prompt version and the model name that produced it.

Results go to a second Kafka topic. Each consuming team has its own consumer group and reads at its own pace;
analytics also loads the topic into the data warehouse every hour.

Documents with a confidence below 0.7 go to a review queue in a labelling tool, where claims staff correct the
claim type. Every month the team replaces the prompt's examples with recent corrected documents, and checks the
new prompt against 2,000 reviewed documents before switching to it.

A dashboard shows, per claim type, the share of documents sent to review and the mean confidence; an alert fires
when the share sent to review for a claim type doubles from one week to the next. Each week, analysts review a
random sample of 300 classified documents.
