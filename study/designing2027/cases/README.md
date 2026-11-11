# Study cases

One folder per case. The folder name is free; the runner reads the case id from `case.yaml`.

```
cases/
  <folder>/
    case.yaml      # id and mode
    problem.md     # the problem: context and requirements (every case)
    solution.md    # the solution to explain (explain cases only)
```

`case.yaml` has two keys:

```yaml
id: kv-store        # lowercase letters, digits and hyphens; names the session (kv-store-E-r1) and the file
mode: search        # search (ddspace-search skill) or explain (ddspace-explain skill)
```

For each session the runner copies `problem.md` into the work copy as `PROBLEM.md` and, for an explain case,
`solution.md` as `SOLUTION.md`. The agent writes `./rationale/<id>.json`. Case ids must be unique.

Write the problem text the same way for every case: a short context, then the requirements as a list. Keep
anything that would hint at the design space (dimension names, ids) out of the problem and the solution, so
the no-space condition (N) reads the same text as E.
