# Methodology

Independent small-scale descriptive study, not a replication of published agentic-code findings.

## Sample and observation

Two mature, public, primarily Python libraries (pallets/flask and psf/requests) were chosen before inspecting maintenance outcomes. Select the two most recently created merged PRs per repository before 2026-09-01, via GitHub issue search sorted by creation time. Contributions must have merged to the observed default branch. This convenience sample includes infrastructure/dependency updates; it is not restricted to production source-code changes. Freeze selected PR numbers and observed default-branch commit SHAs in `reproduction-config.json`.

A 30-day window starts at `merged_at`. If the collection date precedes its end, mark right censoring. Query each tracked path on the pinned branch head through that window. Committer timestamps approximate change time; they are not guaranteed to equal default-branch integration time. Exclude the original merge commit and commits at or before the recorded merge instant. This timestamp approximation can miss or misorder rebased/cherry-picked work.

## Review and origin measures

Only submitted, non-pending reviews at or before merge are considered; exclude the PR author's own reviews. Distinct reviewers are counted by GitHub numeric ID. The latest observed state per reviewer determines approval presence. Historical requested-change events are counted separately. All-time review-comment totals are retained with an explicit scope label and are not treated as pre-merge rigor.

Review indicators operationalize visible process, not latent review quality. Review duration is merge latency, not effort. Bot account type is evidence of automation only. Known dependency-update integration names are labeled separately. A User account, bot-like username, code style, or AI mention is insufficient to establish human/agent authorship; classify unknown. No verified coding-agent contributions or independently verified human-authored cohort are present.

## Candidate maintenance events

Bounded GitHub commit-history queries identify later changes to the same paths. Explicit revert messages must reference the PR number or merge SHA; other labels use conservative message keywords. None prove that the original PR caused a defect. A later security-keyword edit is not a confirmed vulnerability. Renamed/deleted paths, truncated pagination, and untracked files make an observation incomplete. Path attribution is file-level; no blame/introduced-line attribution is implemented.

Use at most 3 file pages, 2 review pages, and 1 history page per tracked path, 100 items per page. At most 5 paths per PR are tracked in the example. Full pages at the cap are conservatively flagged incomplete. Missing API requests fail that PR's collection and are reported as gaps.

## Analysis and validity

Exclude incomplete tracking, incomplete reviews and right-censored windows from binary comparisons. Group by approval presence, report observed fractions and 95% Wilson intervals. Also stratify descriptively by repository and change size (≤100 vs >100 added+deleted lines). The sample has only four small PRs; repository and approval group are confounded here. Contributor experience, review coverage and language variation are not controlled. No regression, matched causal model, statistical-significance claim or defect-rate estimate is justified.

A two-case [assistant-inspected validation spot check](validation-sample.md) demonstrates false attribution risks. It is not an independent human validation or an estimate of classification accuracy.

## Research and API sources

- Xia and Miller (2026), [author manuscript](https://courtney-e-miller.github.io/papers/DoTheseViolentDelightsHaveViolentEnds_MeasuringthePostMergeFateofAgenticCode.pdf): motivates following contributions after merge. Its larger empirical findings are not this project's results.
- [GitHub pull-request reviews](https://docs.github.com/en/rest/pulls/reviews).
- [GitHub commit API](https://docs.github.com/en/rest/commits/commits).

Collectors use credential-free public APIs only, sequential requests, bounded retries, cache provenance, explicit budgets and no downloaded-code execution. Private data and unnecessary author emails are not published.
