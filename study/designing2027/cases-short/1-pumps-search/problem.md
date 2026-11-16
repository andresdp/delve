# Pump failure prediction

## Context

A water utility runs about 400 pumps in 12 pumping stations. Each pump has vibration, temperature and pressure
sensors that report every second. When a pump fails without warning, part of the town loses its water supply, so
the utility wants to replace bearings and seals before they fail. Several stations are in rural areas with an
unreliable mobile connection. The utility has two data scientists and relies on its IT department for servers
and networks.

## Requirements

Functional:

- **R1.** Warn the maintenance team at least 24 hours before a pump is likely to fail, naming the pump and the
  probable cause.
- **R2.** Improve the predictions as technicians record what they find at each inspection.

Quality (as scenarios):

- **Q1 (availability).** When a station loses its connection for up to two days, warnings for its pumps still
  reach the station's on-call technician.
- **Q2 (modifiability).** When a new pump model is installed, its pumps get predictions within one month,
  without changes to how the other pumps are scored.

Constraints:

- **C1.** Sensor data stays on the utility's own premises: no cloud service may store or process it.
