The session prompt of the Designing 2027 study. The runner (`run_sessions.py`) sends one section: `## search`
or `## explain`, by the case's mode, with `{case}` replaced by the case id and `{space}` by the `## space`
section (conditions M and E) or the `## no space` section (condition N). Nothing above the first section is
sent. The text is the same across conditions except for that note and the skill variant; the runner records
this file's SHA-256 in every summary and refuses to mix sessions of two versions in one results folder.

## search

Use the `ddspace-search` skill. The problem, with its context and requirements, is in `PROBLEM.md` in the
working folder. {space}

Design two to four alternative solutions for it, following the skill, with the skill's default budget. Write them as one rationale file,
`./rationale/{case}.json`, with the file id `{case}`, and run `ddspace rationale check rationale/{case}.json`
until it is clean. This is a study session: do not run `ddspace rationale build`.

Use only the files in the working folder, the `ddspace` command and your own knowledge. Do not browse the web,
install packages or call external services. Finish with a short summary of the alternatives.

## explain

Use the `ddspace-explain` skill. The problem, with its context and requirements, is in `PROBLEM.md` in the
working folder, and the solution to explain is in `SOLUTION.md`. {space}

Explain the solution's design decisions, following the skill, with the skill's default budget. Write the explanation as one rationale file,
`./rationale/{case}.json`, with the file id `{case}`, and run `ddspace rationale check rationale/{case}.json`
until it is clean. This is a study session: do not run `ddspace rationale build`.

Use only the files in the working folder, the `ddspace` command and your own knowledge. Do not browse the web,
install packages or call external services. Finish with a short summary of the solution's decisions.

## space

The working folder is a design space: `ddspace query` reads it, and `ddspace point` checks a combination of its
values and describes it. The description comes from a service `ddspace point` calls itself: that call is part of
the tool and allowed, so do not pass `--no-llm` to avoid it.

## no space

There is no design space: work from your own knowledge, as the skill says, and set the file's `space` to
`null`. Do not write a space of your own. Describe each design point with `ddspace point --no-space`, as the skill
says. The description comes from a service `ddspace point` calls itself: that call is part of the tool and
allowed, so do not pass `--no-llm` to avoid it.
