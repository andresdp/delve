You are a software architect. Sketch the architecture of the ML-enabled system described in `BRIEF.md` in
the working folder, as a set of concise Architecture Decision Records (ADRs), one per design decision the
system needs.

Each ADR has, in the required JSON format:

- `decision`: the decision, as a short title or question;
- `context`: why this decision arises for this system (one or two sentences);
- `drivers`: the requirements of the brief that weigh on it (at most three, a few words each);
- `alternatives`: the options you considered (at least two, at most four), each with at most two `pros` and
  two `cons` of a few words each;
- `chosen` and `rationale`: the option you chose and why, given the drivers (one or two sentences);
- `consequences`: what the choice implies or costs (at most three, one short sentence each).

Keep every ADR short: phrases rather than paragraphs. Then list in `uncovered` the decisions the system needs
that you could not ground in what you used.

Use only the files in the working folder and your own knowledge. Do not browse the web, install packages, or
call external services yourself. If the working folder contains an `AGENTS.md`, follow it: it explains the
tools available there, and running them is allowed. Cite the identifiers those tools give you (`citations`,
`value_id`): only identifiers go in `citations`, never titles or prose. Leave `citations` empty and `value_id`
null when you have none. The chosen alternative must be one of the alternatives you list (same label and
`value_id`), and its citations go on that alternative.

Return the ADRs in the required JSON format.
