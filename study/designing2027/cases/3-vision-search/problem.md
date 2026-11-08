# On-device visual inspection

## Context

A manufacturer inspects parts for defects with cameras along its production lines. There are 40 lines in three
plants, each with two to four cameras attached to a small edge computer next to the line. The plants' network is
unreliable: some lines are cut off for days at a time. Quality inspectors label images of defects, about 5,000
new labels a week, and the model is retrained every week from them and pushed to the devices.

The team is two ML engineers and one person who spends half their time on operations. The infrastructure budget
is tight.

## Requirements

Functional:

- **R1.** Check every part as it passes the camera and signal a defective part to the line operator.
- **R2.** Retrain the model every week from the newly labelled images and roll the new model out to every line.
- **R3.** Collect the images the model was unsure about, or got wrong, so that inspectors can label them.

Quality (as scenarios):

- **Q1 (latency).** Each image is classified on the line within 200 ms, so the line never slows down.
- **Q2 (availability).** When a plant's network is down for up to seven days, its lines keep inspecting with the
  model they have; the images collected in the meantime are uploaded when the network returns.
- **Q3 (deployability).** A new model reaches every connected line within 24 hours of approval. When a new model
  misbehaves on a line, the line operator can go back to the previous one within 15 minutes, without the ML team.
- **Q4 (cost).** Cloud and infrastructure spending stays under 2,000 euros a month.

Constraints:

- **C1.** Three people build and run the system, with no support outside working hours.
- **C2.** The edge computers (an ARM processor with a small neural accelerator) cannot be replaced this year.
