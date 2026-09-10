# Pre-submission reviewer-perspective review

This review was performed before the final mechanical checks (citation order,
figure/table cross-references, rendering). It evaluates the manuscript as an
adversarial reviewer would, across five domains, and ranks each finding by
severity, corrective value, and feasibility with current data. Findings judged
blocking were addressed in the manuscript before finalization; residual
limitations that cannot be resolved with current data are stated openly in the
text.

Target journal: *Transport Economics and Management* (Elsevier, open access), Research article.

## 0. Retargeting review (TEM, 9 September 2026)

The RTBM desk rejection cited "limited transport impact and implications".
This is a positioning problem, not a data problem, and it is the most likely
desk-reject trigger at TEM as well. Findings and actions:

- **Finding (highest) — the paper read as a privacy/security audit that happened
  to use transport data.** Addressed: the Introduction now frames the
  city-operator relationship as a principal-agent contract under information
  asymmetry, in which public disclosure is the lowest-cost information a
  procuring body can observe; the Abstract carries the same framing; the
  Discussion adds a paragraph locating where the asymmetry is largest
  (end-of-life stages: near-domain evidence *and* document silence) and what
  that implies for the cost of contractual monitoring; Section 4.2 is retitled
  "Implications for transport management and concession design" and now ties
  the indicators to tender scoring and permit renewal.
- **Finding (high) — economic framing must not outrun the evidence.** The
  study measures disclosure, not costs, prices, or welfare. The added text is
  explicitly qualitative (where verification is cheap vs. where it requires
  audit/reporting clauses) and does not claim to estimate compliance costs or
  contract outcomes. No quantitative economic claim was added.
- **Finding (medium) — keywords.** TEM allows at most six; "transport
  management" (multiword, general) and "lifecycle exposure" (jargon) were
  dropped in favour of "concession design", which matches the new framing.
- **Finding (medium) — citation style.** TEM uses numbered references in
  order of first appearance; the whole pipeline was switched from APA
  author-date to `[n]` numbering, with the reference list reordered
  automatically and validated (no orphans, numbers within range, list order
  equals first-appearance order). The public `reproduce.py` reads the
  committed `results/citation_order.json` so the standalone editable tables
  carry the same numbers.
- **Finding (low) — figures.** The TEM guide asks for each illustration as a
  separate file; figures are therefore supplied separately (PNG/TIFF/PDF +
  editable PPTX) with captions placed at first mention in the text. Tables
  remain inline and editable, with horizontal rules only and no shading.
- **Residual risk.** TEM's editorial board may still judge a disclosure audit
  to be outside "economics and management" proper. The cover letter therefore
  states the fit explicitly (operator benchmarking, tender scoring, concession
  monitoring) and the Highlights foreground the management use of the
  indicators. If desk-rejected again on scope, the next candidate should be a
  policy/governance venue rather than another business-management journal.

## 0b. Second reviewer-perspective pass (journal fit, 9 September 2026)

A second adversarial read of the TEM-retargeted manuscript, ranked by
desk-reject risk. All items marked "implemented" are in the current build.

- **Highest — no engagement with transport economics/management literature.**
  The Introduction asserted that "transport economics and management
  scholarship has long examined fleet deployment, concession design, and risk
  allocation" with zero citations, and the principal-agent claim had no
  anchor. A TEM referee would read this as a security paper wearing a
  transport label. *Implemented:* six verified references added (Crossref
  metadata and DOI resolution checked, recorded in
  `output/Reference_Verification.csv`): Gössling 2020 (TR-D) and Button et al.
  2020 (Res. Transp. Econ.) on e-scooter regulation; Docherty et al. 2018 and
  Pangbourne et al. 2020 (TR-A) on smart-mobility governance and platform
  control of data; Cottrill 2020 (TR-A) on MaaS privacy; Hart, Shleifer &
  Vishny 1997 (QJE) for the incomplete-contracting argument that
  contracted-out public services under-deliver on hard-to-verify quality.
  The cover letter now names these literatures.
- **High — unsupported cost language.** "Lowest-cost information", "at
  negligible cost", and "impose compliance costs" were asserted without any
  cost data. *Implemented:* rephrased throughout (Abstract, Introduction,
  Discussion, 4.1) to the verifiable claim that public disclosure is what a
  principal can observe *without operator cooperation*; an explicit sentence
  states that costs and welfare effects were not measured and that the
  principal-agent framing is an interpretive lens, not a tested model. Same
  point added to Limitations (no contracts, tender scores, costs, or prices
  were observed).
- **High — WP3 sampling rule unstated.** Methods said only "we selected
  operators from the audited GBFS population"; with n = 13 a referee will ask
  how. *Implemented:* Methods now states the prespecified rule from
  `PROTOCOL.md` / `audit/operator_sample.csv` (top-N operator domains by
  number of eligible motorized systems, ties alphabetical, N read from the
  data), and Limitations notes that the sample is small relative to the
  population of operator domains and that smaller operators may disclose
  differently.
- **Medium — Abstract carried no effect sizes for RQ2/RQ3.** *Implemented:*
  the Abstract now reports identifier, position, and battery prevalence and
  the operator-notice counts, all pulled from the results files (249 words,
  under the 250-word gate).
- **Medium — Table 3 omitted two fields that the text reports (current range,
  rental link).** *Implemented:* both rows added from `results/gbfs_summary.csv`
  so every prevalence quoted in 3.2 is in the table.
- **Medium — Table 2 study labels inconsistent** ("Casagrande et al" without
  period vs. "Petersen (2019)"). *Implemented:* labels now come from the
  shared `CITEMETA` author strings.
- **Medium — section order.** Limitations preceded Implications, so the paper
  ended its Discussion on a policy pitch rather than on its caveats.
  *Implemented:* 4.1 Implications, 4.2 Limitations.
- **Optional (not implemented, needs new data).** An inter-rater reliability
  check on the WP3 coding, and a panel of operators over time to test whether
  disclosure indicators predict contract outcomes. Both are stated as future
  work rather than claimed.

## 1. Manuscript (novelty, focus, logic, method completeness)

- **Strength.** The package answers three linked questions (direct evidence,
  public field prevalence, disclosure completeness) with an explicit,
  reproducible method chain rather than a conceptual argument. This directly
  answers the earlier desk-rejection reasons (insufficient direct evidence,
  weak method, irreproducible synthesis).
- **Finding (medium).** The paper is short (~2,300 words of prose). This is
  acceptable for a focused empirical contribution and is preferable to padding
  that would risk overclaiming; the evidence base genuinely bounds the length.
  No change made.

## 2. Statistical / measurement design

- **Finding (high) — analysis unit and independence.** Because a few operators
  run many city systems, system-level prevalence could be driven by a handful
  of operators. Addressed: an operator-domain sensitivity analysis (147 eligible
  domains) is reported alongside the system-level figures, and both are shown.
- **Uncertainty.** All proportions are reported against explicit denominators
  with 95% Wilson confidence intervals (Table 3, Fig. 3). Unavailable/empty
  feeds are separated from feeds that omit a field.
- **Finding (high) — screening is not inter-rater reliability.** The delayed
  20% rescreen (n = 447, 100% agreement) demonstrates *computational
  reproducibility* of a deterministic rule set, not inter-rater reliability.
  The manuscript states this explicitly in Methods and Limitations.

## 3. Figures and tables

- Five figures and five tables, each cited in first-appearance order. Tables
  are placed inline immediately after first mention; figure captions are placed
  at first mention and the figure files are supplied separately as the journal
  requires; also delivered as editable PPTX (one figure per slide) and editable
  DOCX tables.
- **Finding (medium) — evidence map informativeness.** The evidence map (Fig. 2)
  originally collapsed each study to its first-listed lifecycle stage, dropping
  two D2 studies and flattening the map onto "operation". Fixed: studies are now
  counted in every lifecycle stage they address, which correctly surfaces the
  D2-heavy recall/return and second-life/disposal cells that the narrative
  relies on. Caption and axis label updated accordingly.
- No redundant or decorative figures; each supports a specific claim.

## 4. Reproducibility and provenance

- The GBFS registry snapshot is frozen and checksummed; screening decisions,
  coding sheets, and all generation code are committed. Counts in the text are
  regenerated by `build_submission.py` from `results/gbfs_summary.csv`,
  `data/document_audit.csv`, and `review/evidence_extraction.csv`.
- **Finding (high) — honest reference verification.** The reference-verification
  report previously hard-coded "verified". Fixed: it now performs a live DOI/URL
  resolution check (with a graceful offline fallback) and records the actual
  outcome per reference. All 30 references resolve to real records (HTTP 200/202;
  a few ACM/publisher DOIs return 403 anti-bot responses that still confirm a
  live record; three entries are standards/regulations without a DOI).
- **Highest-priority caveat — document-audit validation.** The 14-domain
  document coding is produced by deterministic text matching and reviewed by a
  single reviewer. Regex matching can over- or under-classify generic mentions.
  Every cell carries a short verbatim locator quotation so a third party can
  check it, and the manuscript frames the results as coding of public documents,
  not as verified operator practice. This remains the main item a second
  independent coder should re-check before a revision.

## 5. Strength of claims vs. evidence

- The manuscript consistently frames published fields and document silence as
  *disclosure/evidence signals*, explicitly not as harm, compromise, or
  regulatory violation.
- `not_found` is defined as document silence, never as proof of absence.
- The lifecycle controls are labelled proposals whose effectiveness was not
  tested; Table 5 records effectiveness evidence conservatively.
- End-of-life (recall/return, second-life/disposal) evidence is visibly marked
  as near-domain (D2) in both Fig. 2 and Fig. 5 (dashed boxes).

## Priority summary

**Highest priority (must hold before submission)**
- Document-audit claims must stay bounded to "coding of public documents" with
  per-cell quotations; do not assert operator practice. — Held in text.

**High priority (addressed)**
- Operator-domain sensitivity analysis reported. — Done.
- Screening described as computational reproducibility, not IRR. — Done.
- Reference verification made honest via live resolution. — Done.

**Medium priority (addressed)**
- Evidence map now multi-stage and informative. — Done.
- Public field presence clearly distinguished from backend collection and harm.
  — Held in text.

**Optional / for a future revision**
- Add a second independent coder for the document audit to obtain inter-rater
  reliability.
- Consider shortening the title if the journal flags length at submission.

## 0c. Final pre-submission audit (9 September 2026)

Scope: mechanical and content checks requested before packaging. Findings are
listed with what was changed; anything not listed passed unchanged.

| Check | Result | Action |
|---|---|---|
| Figures/tables cited before first appearance, in order | Fig. 1-5 and Table 1-5 first mentioned in order; each placed after its citing paragraph | none |
| References numbered by first appearance, no orphans | 36 refs, sequential, all cited | none |
| Every reference exists | 30 DOIs verified against Crossref/DataCite registered titles; 6 non-DOI sources (GBFS, systems.csv, OMF guide, EDPB 01/2020, EU 2023/1542, GDPR) verified on official pages | added official URLs to the 4 non-DOI refs that lacked one; verifier now records the registered title |
| Equations as Word-native math | Wilson interval rendered as OMML (editable in Word), no literal LaTeX | added `add_equation`/`wilson_omml` |
| No 2-byte characters | Manuscript, tables, title page, highlights, cover letter, PPTX slide text are ASCII-only (the only non-ASCII glyphs are the +/- and hat symbols inside the OMML equation object) | folded two accented author names (Gossling, Mladenovic); replaced curly quotes in the cover letter |
| Numbers traceable to data | All 78 scalar values in `reproducibility_values.json` appear verbatim in the manuscript; screening (2,169/1,945/224/18 = 5 D4 + 9 D3 + 4 D2), GBFS and document-audit counts re-derived from the committed CSVs | replaced a vague "explicit for most" with the data-derived count |
| Public-copy reproduction | `reproduce.py` in a clean copy of tracked files: 5/5 tables identical, 5/5 PNG byte-identical | none |
| Intro -> Results/Discussion | RQ1-3 each answered in 3.1-3.3 and revisited in Section 4; both stated gaps (evidence map; lifecycle disclosure) are closed | none |
| Discussion vs Results | Claims checked sentence-by-sentence against Table 3/4 counts; no causal language beyond "indicates/points to"; effectiveness of controls and cost/welfare explicitly not measured | none |
| No "previous version" language | none found | none |
| Style | mixed -ise/-ize spelling unified to -ize; one awkward sentence in 3.2 reworded; Limitations now state the WP3 sampling rule consistently with Methods | edits in `build_submission.py` |

Residual reviewer-visible limitations (unchanged, disclosed in 4.2): single
reviewer, 13 coded notices, cross-sectional feeds, interpretive principal-agent
framing, unvalidated controls.
