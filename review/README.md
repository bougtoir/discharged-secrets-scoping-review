# Review workspace

This directory contains reproducible search and screening materials for the scoping-review component.

## Build the initial candidate corpus

```bash
python review/search_open_metadata.py \
  --config review/search_queries.json \
  --output review/candidates.csv \
  --log review/search_log.csv
```

The initial search uses OpenAlex and Crossref metadata from 1 January 2010 onward. IEEE Xplore, ACM Digital Library, arXiv, official-source searches, and citation chasing are logged separately during full screening.

`candidates.csv` is a search result, not the included evidence set. Inclusion decisions belong in a separate screening table with explicit reasons.
