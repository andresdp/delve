# Quickstart: a design space from a small example

This walks through `ddspace` on one of two small examples that ship with the repository:

| Example | Folder | Documents | Use case |
|---|---|---|---|
| Pharmacy food | [`examples/pharmacy-food/`](examples/pharmacy-food/) | 12 architecture decisions | A "ghost kitchen" healthy-food startup |
| Campus bike | [`examples/campus-bike/`](examples/campus-bike/) | 28 architecture decisions | CityBike, a bike-sharing platform |

Each example is a JSON list of short decision statements plus a pipeline config with its use case. Pharmacy
food is the smallest and cheapest; campus bike gives a richer design space. The steps are the same; only the
two file paths change.

## 1. Install

From the repository root, in your Python environment (3.10 or newer):

```bash
pip install -e ".[chat]"     # [chat] adds ddspace ask (TreeDex); leave it out if you do not need it
ddspace --version
```

The tool uses OpenAI by default, for the LLMs (`gpt-5.6-luna`) and for the embeddings
(`text-embedding-3-small`). Embeddings are required: they merge duplicate values, merge near-duplicate
dimensions and link each value to its supporting passages. One `OPENAI_API_KEY` covers both. Export it, or
let `ddspace init` write it to the workspace's `.env`:

```bash
export OPENAI_API_KEY=sk-...
```

## 2. Create a workspace

Work outside the repository, for example in your home folder. `--from-config` takes the use case, the models,
the dimension cap and the batch size from the example's config; `--yes` skips the questions.

```bash
cd ~
ddspace init pharmacy --yes --from-config <repo>/examples/pharmacy-food/pharmacy_food_config.yaml
cd pharmacy
```

Campus bike: `ddspace init campus --yes --from-config <repo>/examples/campus-bike/campus_bike_config.yaml`.

Replace `<repo>` with the path to your clone. Without `--yes`, `init` asks a few questions instead. Every
setting is in `ddspace.yaml`, with a comment each.

## 3. Add the sources

Your own sources are files you put in `sources/` (`.md`, `.txt`, `.html`, `.pdf`). The examples are JSON
corpora instead, so import them: each decision becomes one source file.

```bash
ddspace sources --from-json <repo>/examples/pharmacy-food/pharmacy_food_architecture_decisions.json
```

Campus bike: `--from-json <repo>/examples/campus-bike/campus_bike_architecture_decisions.json`.

`ddspace sources` lists every source with its word count, then splits the sources into passages
(`corpus.json`): 12 passages for pharmacy food, 28 for campus bike. The decisions are a few dozen words each, so
they are all flagged `short`; that is expected here and they are still used. (`--no-corpus` only scans;
`ddspace corpus` rebuilds the passages with other sizes.)

## 4. Mine the design space

```bash
ddspace mine
```

`mine` first shows the corpus size, the models and an estimate of tokens and time, and asks before it starts.
For these examples the run takes a few minutes. The console shows one progress line (the current step and the
elapsed time); the pipeline's full output goes to `runs/<time>/pipeline.log`. Add `--verbose` to see the full
output instead. To spend less, create the workspace with `--no-critic` (no evaluation scoreboard during the
run).

When it finishes, `mine` prints the number of dimensions and values, the tokens used and the time taken.

## 5. Build and browse the wiki

```bash
ddspace wiki build --yes
ddspace wiki open
```

This writes:

- `wiki/`: the design space as Markdown, an Open Knowledge Format (OKF v0.2) bundle (start at `wiki/index.md`;
  it also opens as an Obsidian vault);
- `site/`: the same as HTML, with the interactive graph (`site/graph.html`) and tree (`site/tree.html`);
- `raw/graph.json`: the data `ddspace query` reads.

`--yes` takes the defaults: quoted passages on, no source summaries, sampled design points without
descriptions (no extra LLM calls). Without `--yes` it asks; the answers are saved under `wiki:` in
`ddspace.yaml`. `ddspace wiki check` checks the bundle against OKF.

## 6. Ask questions

From the command line (read-only, no LLM):

```bash
ddspace query dims --table
ddspace query values "<a dimension name>" --table
ddspace query evidence "<a value name>" --quotes --table
ddspace query relations --table
```

Names can be ids (`d:3`, `v:3.1`), slugs or labels; a unique part of a label also works.

With the built-in chat (the mining LLM answers from the wiki; about two LLM calls per question):

```bash
ddspace ask "Which alternatives exist for handling payments, and which decisions support them?"
```

It lists the wiki pages it used and the passage ids it cites. Each `ddspace wiki build` rebuilds its index.

Through a coding agent (Claude Code, GitHub Copilot in agent mode):

```bash
ddspace agent setup --claude --copilot
```

Then open the workspace folder in the agent and ask, for example: *"What are the alternatives for payment
processing, and which decisions support each? Cite passages."* The agent reads `AGENTS.md`, runs
`ddspace query`, and cites passage ids such as `s04_p01`.

## 7. Refine and start over

```bash
ddspace update --feedback "Merge the two data-access dimensions"   # re-mine, seeded with the current design space
ddspace wiki build --yes                                           # wiki/log.md records what changed
ddspace check                                                      # configuration, missing items, progress per phase
ddspace reset                                                      # archive runs and wiki; sources and settings stay
ddspace reset --purge                                              # delete everything except ddspace.yaml and .env
```

Every command has `--help`. [USAGE.md](USAGE.md#the-ddspace-command) describes all of them.
