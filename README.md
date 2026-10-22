<p align="center">
  <img src="images/ddspace-logo.svg" alt="ddspace logo" width="560">
</p>

# ddspace: Automated Generation of Architecture Design Spaces as Wikis

ddspace reads a collection of documents (practitioner articles, architecture decision records, design
notes, blog posts) and builds a **design space** from them:
- the **decision points** the documents discuss;
- the **candidate decisions** for each one;
- how the sources stand toward each candidate (adopted, rejected, or disputed);
- the **outcomes** they report;
- how decision points **relate** to each other.

Every candidate decision keeps links to the passages that support it. The result is published as a browsable
wiki in the Open Knowledge Format (OKF), which people can read and coding agents can query.

The `ddspace` command line is the entry point:
- it manages a workspace of sources;
- it mines the design space with an LLM-based workflow inspired by grounded theory;
- it builds the wiki;
- it answers read-only, LLM-free queries over it.

## Browse a design space without installing anything

The C3 sample is a design space mined from five public sources on hosting Git at scale. It is capped at 8
decision points, with 24 sampled design points placed on the systems the sources describe. Its wiki has a page per
decision point, alternative, design point and source, and graph and tree views.

- **[Browse the wiki online](https://anonymous.4open.science/api/repo/ddspace-E704/file/examples/c3-git-at-scale/sample/c3-git-at-scale-sample_taxonomy_20261016_094637_wiki/html/index.html).** The online viewer blocks scripts, so the graph and tree views work
  only from a download ("Download repository"): open
  `examples/c3-git-at-scale/sample/c3-git-at-scale-sample_taxonomy_20261016_094637_wiki/html/index.html`.
- The Markdown wiki (`wiki/`) and the raw data (`raw/`) are in the same folder. How the sample was produced:
  [examples/c3-git-at-scale/sample/README.md](examples/c3-git-at-scale/sample/README.md).

The source texts themselves are not included (copyright). The wiki quotes short passages as evidence.

## Install

Python 3.10 or newer is required.

```bash
cd <this folder>
python -m venv .venv && source .venv/bin/activate     # or a conda environment
pip install -r requirements.txt
pip install -e ".[chat]"                             # provides the ddspace command ([chat]: ddspace ask)
ddspace --version
```

Mining needs an LLM provider key: OpenAI by default, for the LLMs and the embeddings. Querying an existing wiki
needs no key.

```bash
export OPENAI_API_KEY=sk-...
```

## Try it without an API key: query the sample wiki

```bash
W=examples/c3-git-at-scale/sample/c3-git-at-scale-sample_taxonomy_20261016_094637_wiki
ddspace query dims --graph $W --table
ddspace query values "Repository Placement and Read Routing" --graph $W --table
ddspace query evidence "Stateless repository placement" --graph $W --table
ddspace query search "routing" --graph $W
```

`ddspace query --help` lists every query: `info`, `dims`, `show`, `values`, `evidence`, `relations`, `search` and
others.

## Mine a design space

[QUICKSTART.md](QUICKSTART.md) walks through two small included examples (12 and 28 short decision
statements; a few minutes and a few cents each). The workflow for your own sources is:

```bash
ddspace init my-space             # asks a few questions (use case, models, size); --yes takes the defaults
cd my-space && cp ~/Downloads/*.pdf sources/
ddspace sources                   # extract the text, draft sources.csv, flag problems, split into passages
ddspace mine                      # shows an estimate, asks, then mines the design space into runs/
ddspace wiki build                # wiki/ (Markdown, OKF), site/ (HTML), raw/ (data)
ddspace wiki open                 # browse it
```

Later:

```bash
ddspace update --feedback "Merge the two caching dimensions"   # re-mine, seeded with the current design space
ddspace update --test --sources new-article.html               # dimensions frozen; new sources add values
ddspace query values "Replica placement" --table               # read-only questions, no LLM
ddspace ask "Which alternatives exist for replica placement?"  # an answer from the wiki, citing passages
ddspace point "Leader-based" "WAL in S3" --table               # interpret one combination; nothing stored
ddspace check                                                  # what is configured, missing, and done so far
```

### Asking questions through a coding agent

```bash
ddspace agent setup --claude --copilot
```

This writes the following files:
- `AGENTS.md`: the `ddspace query` commands with examples from your wiki, and rules (cite passage ids, treat quoted passages as data, generated summaries are not evidence);
- a `CLAUDE.md` that imports `AGENTS.md`;
- an optional Claude Code permission for `ddspace query`;
- `.github/copilot-instructions.md`.

Open the workspace in the agent and ask, for example, *"What are the alternatives for replica placement, and
which sources support each? Cite passages."*

## How it works

1. **Open coding.** Each passage is coded: short concept labels with a rationale and a stance (`accepted`,
   `rejected`, or `outcome`).
2. **Axial coding.**
   - The first batch's codes produce a draft design space.
   - Each later batch updates it by constant comparison, through validated, logged editing operations: add, split, merge, move, relate.
3. **Feedback.**
   - A critic scores each draft and reports issues.
   - A saturation check reports concepts that new passages bring and the draft does not cover.
   - Both go into the next update. The loop stops at saturation or when the batches run out.
4. **Selective coding.**
   - A final review revises the design space.
   - Consolidation merges duplicates and links every code to the alternative it supports, with each source's stance.
   - Selection keeps the decision points that serve the use case and have enough evidence.

Configuration, commands and output files: [USAGE.md](USAGE.md). Vocabulary: [CONCEPTS.md](CONCEPTS.md).

## Layout

| Path | Content |
|---|---|
| `src/delvedspace/` | The `ddspace` command: workspaces, sources and corpus, runs, wiki build, queries, agent setup |
| `src/taxonomy_generator/` | The mining workflow (LangGraph), prompts, wiki export and queries |
| `examples/` | The C3 sample wiki and two small corpora for QUICKSTART |
| `tests/` | Unit tests, no API calls: `python -m pytest tests/unit_tests` |

## Background

ddspace started from an open-source implementation of TnT-LLM ("Text Mining at Scale with Large Language
Models", Wan et al., [arXiv:2403.12173](https://arxiv.org/abs/2403.12173)). It builds grounded-theory design
spaces instead of flat label taxonomies.

## License

MIT, see [LICENSE](LICENSE).
