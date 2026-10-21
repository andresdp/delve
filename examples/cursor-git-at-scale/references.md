# References

## Primary source

- Vicent Martí, ["Git at any scale"](https://cursor.com/blog/git-at-any-scale), Cursor blog, 2026.
  Source article for all 16 documents in this corpus; the basis for the description of GitHub's
  filesystem experiments, Google's JGit/DHT attempt, GitHub's Spokes, and Cursor's Continuity/Origin.

## Supplementary background (used to add context the primary source assumes as known)

- GitHub Engineering, ["Stretching Spokes"](https://github.blog/engineering/infrastructure/stretching-spokes/) —
  background on why Spokes replaced DRBD block-level replication, and the geo-replication scaling
  problems (network round-trip latency, reference-update volume) GitHub solved as it grew past ~70
  million repositories. Used in `decision-github-spokes-consensus-replication.md` and
  `evolution-timeline-of-git-hosting-decisions.md`.
- GitHub Engineering, ["Building resilience in Spokes"](https://github.blog/engineering/infrastructure/building-resilience-in-spokes/) —
  additional background on Spokes' operational hardening. Referenced for context only.
- Microsoft, [Scalar philosophy document](https://github.com/microsoft/git/blob/vfs-2.37.3/contrib/scalar/docs/philosophy.md) —
  rationale for Scalar's narrow scope (partial clone, sparse-checkout, background maintenance) and its
  deliberate move away from the older GVFS virtualization protocol. Used in
  `decision-microsoft-gvfs-and-scalar.md`.
- Microsoft Azure DevOps Blog, ["Introducing Scalar"](https://devblogs.microsoft.com/devops/introducing-scalar/) —
  architecture and benchmark details (e.g., the Windows OS repository's ~90M objects / 100GB compressed
  history, GVFS protocol cache servers). Used in `decision-microsoft-gvfs-and-scalar.md`.
- Wikipedia, ["Rendezvous hashing"](https://en.wikipedia.org/wiki/Rendezvous_hashing) — background on the
  highest-random-weight hashing technique Continuity uses for stateless repository-to-node routing.
  Used in `decision-cursor-continuity-wal-in-s3.md`.

## Note on secondary write-ups of the same article

A few independent blogs and explainers have also summarized the Cursor post (e.g., XiaoHu AI's
"How Cursor rebuilt Git hosting to tackle a 20-year-old problem" and explainx.ai's "Cursor Origin: How
Its New Git Hosting Actually Works"). These were not used as sources here — everything in this corpus
was derived directly from the primary Cursor article and the official background documents listed
above, to avoid compounding any drift introduced by third-party retellings.
