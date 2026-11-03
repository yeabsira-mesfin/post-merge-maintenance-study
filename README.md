# Post-Merge Maintenance Study

**How do observed review practices relate to subsequent maintenance activity?**

An independent small-scale GitHub research instrument, with Python collection and analysis plus a React + TypeScript evidence dashboard. This reuses `React-` and preserves its history. Intended name: `post-merge-maintenance-study`. The existing repository visibility is unchanged until explicitly changed in GitHub settings.

## Working capabilities

- Reproducible, bounded selection of merged PRs with a fixed cutoff and pinned default-branch heads.
- Pre-merge review counts, distinct reviewers, approval status, change requests, merge latency and PR size.
- Conservative provenance: Bot metadata supports automation; a User account remains unknown authorship. Routine dependency bots are distinct from coding agents.
- Thirty-day file-history tracking, candidate fix/revert/refactor/security keyword events, censoring and incomplete-data flags.
- Descriptive approval-group comparisons, Wilson uncertainty intervals, and repository/size strata.
- JSON/CSV/SQLite exports, source-linked event inspection, React filters and Vercel-ready static configuration.

## Run

```bash
# Python 3.12+ standard library; Node 22+
npm ci --ignore-scripts
npm run dev
python -m research.study
python -m research.analyze
python -m unittest discover -s tests -v
npm run build
```

The real example contains four PRs from pallets/flask and psf/requests. Two have recorded approval and two do not; one in each group has a later file edit in the complete 30-day window. This tiny descriptive comparison **is not evidence of a review-quality effect**. Three contributions have unknown origin; one is verified routine automation, so no AI-versus-human comparison is supported.

The [two-event validation spot check](docs/validation-sample.md) found a documentation correction and a routine tool-version update. Neither establishes a defect introduced by the tracked PR.

See [methods](docs/methodology.md), [reproduction](docs/reproduction.md), [limitations](docs/limitations.md), [architecture](docs/architecture.md), [QA](docs/qa-report.md) and [Vercel setup](docs/deployment.md). MIT-licensed code; upstream public metadata remains attributed to its sources.

Related: [AgentBench Research Edition](https://github.com/yeabsira-mesfin/JavaScript) · [Dependency Health Observatory](https://github.com/yeabsira-mesfin/React).

## Related work

Chunqiu Steven Xia and Courtney Miller. *Do These Violent Delights Have Violent Ends? Measuring the Post-Merge Fate of Agentic Code*. 2026 preprint, listed as under review on the author's publication page. [Author manuscript](https://courtney-e-miller.github.io/papers/DoTheseViolentDelightsHaveViolentEnds_MeasuringthePostMergeFateofAgenticCode.pdf). This project does not copy their implementation or dataset and does not claim a replication of their findings.
