# Event-attribution validation sample

Inspected on 2026-11-03 by the implementation assistant, by reading the actual GitHub commit diffs. This is a two-case spot check, not an independent human-coded validation dataset or precision estimate.

| Tracked PR | Later commit | Automatic label | Diff inspection | Interpretation |
|---|---|---|---|---|
| pallets/flask #6096 | [d73fa1c](https://github.com/pallets/flask/commit/d73fa1cdcbd8b1465c151db8924ba58b1dd14e35) | fix-keyword edit | Corrects two Sphinx cross-reference delimiters in `src/flask/app.py` docstrings. | Documentation correction. No evidence here that PR #6096 introduced a runtime defect. |
| psf/requests #7608 | [dae7ef6](https://github.com/psf/requests/commit/dae7ef63b4df6eded86637f251fc4e3a06c3b479) | later file edit | Updates the Ruff pre-commit pin from v0.16.3 to v0.16.4. | Routine version update, not evidence that the earlier dependency update was defective. |

These examples illustrate why file overlap and commit-message keywords must remain candidate event signals. Neither case has line-level attribution to the earlier PR. Two spot checks cannot validate the sensitivity or specificity of the heuristic. A future study should freeze a random validation sample and use multiple independent reviewers with adjudication.
