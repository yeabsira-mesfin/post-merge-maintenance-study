# Reproduction

```bash
npm ci --ignore-scripts
python -m unittest discover -s tests -v
python -m research.analyze                 # exact committed observations; no network
python -m research.study --config reproduction-config.json
npm run build
npm run preview
```

Python 3.12+ standard library, Node 22+. The committed JSON contains the chosen PR IDs, source URLs, observation timestamps, pinned default-branch heads, events, analysis and incomplete-data flags. `research.analyze` recomputes the comparison from that snapshot without API access.

`sample-config.json` reruns the original bounded sampling query. `reproduction-config.json` freezes PR IDs and branch heads. Live review metadata may still be edited; compare provenance hashes. `--cache` selects the local raw JSON cache. `--offline` requires a populated cache; `--refresh` recollects. Cache files and SQLite are local and ignored by Git. A CSV and SQLite database are written next to the JSON.

The example's four PRs are Flask #6133/#6096 and Requests #7609/#7608. Follow-up is 30 days per merge. All four are complete and uncensored in the committed example. Both approval groups contain two PRs; one PR per group has a later edit, yielding 0.5 observed proportions and Wilson intervals [0.0945, 0.9055]. These are descriptive results only. Updating the dataset requires regenerating the JSON and rebuilding Vercel.
