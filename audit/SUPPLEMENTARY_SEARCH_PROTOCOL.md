# Supplementary operator-document search — protocol

This protocol was finalized before the supplementary search results were
examined; it is a prospective specification, not a formal external
preregistration.

Added in response to peer review (Reviewer 2, comment 3): absence from a privacy
notice does not establish absence from other public operator documents. This
targeted, reproducible search extends the same 15-operator sample to a bounded
set of other public documents. It is a supplementary sensitivity/extension
analysis; it does not change the original WP3 privacy-notice coding.

## Population

The 15 operator website domains in `audit/operator_sample.csv` (unchanged
sample).

## Documents sought per domain

1. `https://<domain>/.well-known/security.txt`
2. `https://<domain>/security.txt`
3. The operator homepage `https://<domain>/` (or the document URL recorded in
   `data/document_audit.csv`), followed by up to 8 same-registrable-domain
   links whose URL path or anchor text matches one of:
   `privacy|terms|legal|security|vulnerab|disclos|responsible|sustainab|recycl|
   return|imprint|policy|cookie|data`
4. One second-level hop from each fetched page is allowed if it is needed to
   reach a document matching the same pattern (bounded crawl, max 25 requests
   per domain).

## Recording

Every HTTP request that returns content is stored verbatim under
`data/raw/operator_docs/<domain>/` and logged in
`data/document_search_ledger.csv` with: operator domain, URL, document-type
guess, HTTP status, UTC fetch time, bytes, SHA-256, and the local path. Pages
that fail or redirect off-domain are recorded as unavailable with status.

## Coding (deterministic)

Two domains relevant to Reviewer 2's comment are coded on the *fetched
document set*:

- **vulnerability-disclosure channel**: presence of a `security.txt`, or text
  matching `vulnerability|responsible disclosure|coordinated disclosure|
  bug bounty|report.*security|security@` in any fetched document;
- **device return / recycling / disposal**: text matching
  `recycl|end[- ]of[- ]life|second life|dispos|return.*(vehicle|scooter|bike|
  device|battery)|take[- ]back` in any fetched document.

Each positive is recorded with the source URL and a short verbatim snippet in
`results/supplementary_document_search.csv`. A domain in which no matching
document could be fetched is coded `unavailable`, not `not_found`.

## Limits stated in the manuscript

This is a bounded crawl of each operator's public website on a single date,
not an exhaustive search of all public documents (app-store listings,
regulatory filings, tenders, or help-centre platforms hosted on third-party
domains are outside the crawl boundary). Results are reported as
supplementary sensitivity findings only.
