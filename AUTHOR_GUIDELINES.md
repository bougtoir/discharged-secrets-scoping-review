# Transport Economics and Management submission requirements checked on 9 September 2026

Target journal: **Transport Economics and Management** (Elsevier, ISSN 2949-8996), fully open access, double-anonymized peer review.

## Scope and article positioning

Transport Economics and Management publishes research on transportation business, management, economics, strategy, and economic policy across all modes, including operations management, management information systems, sustainability, finance, logistics, marketing, franchising, privatisation, and commercialisation. This manuscript is submitted as a **Research article**. It contributes:

1. a PRISMA-ScR evidence map of direct data-exposure evidence in shared micromobility;
2. a global, privacy-preserving audit of what public GBFS vehicle feeds actually disclose;
3. a structured audit of public operator lifecycle-disclosure documents; and
4. a reproducible lifecycle exposure model that frames the city-operator relationship as a contract under information asymmetry and links evidence strength to procurement, concession-design, and risk-allocation choices.

## Format

- **Research article**; no explicit word limit is stated in the guide, so the manuscript stays concise (main text about 2,800 words).
- **Abstract**: concise and factual, able to stand alone, no references; nonstandard abbreviations used in the abstract are defined at first mention there and again in a first-page footnote.
- **Highlights** (encouraged): 3-5 bullets, each no more than 85 characters including spaces, supplied as a separate file.
- **Maximum 6 keywords**, American spelling, avoiding general/plural terms and multiword concepts containing "and" or "of".
- **Numbered sections** (1., 1.1, 1.1.1, ...); the abstract is not numbered.
- **Numbered references**: in-text citations are numbers in square brackets in order of first appearance (`[3]`, `[3,5]`, `[3-6]`); the reference list is ordered by number, not alphabetically. Journal abbreviations follow the List of Title Word Abbreviations; DOIs are given as full `https://doi.org/` links. Dataset references carry the `[dataset]` prefix.
- The manuscript file is **anonymized** (double-anonymized peer review); author details, full postal address, corresponding-author email, present/permanent address, and funding appear only on the separate title page and cover letter.

## Required declarations

Placed after the main text and before the references:

- **CRediT authorship contribution statement** (withheld while blinded; restored on acceptance);
- **Declaration of generative AI and AI-assisted technologies in the writing process** (language editing only, using the journal's wording);
- **Funding** (journal wording for no funding);
- **Declaration of competing interest** (journal wording);
- **Data availability**.

Additionally supplied as good practice: acknowledgements (withheld while blinded) and an ethical-standards statement.

## Figures and tables

- Five figures and five tables, each cited in the body before or at first appearance. Tables are placed inline immediately after the paragraph of first mention; figure captions are placed at first mention and the figure files are supplied separately, as the guide asks for each illustration as a separate file and the manuscript in a self-contained editable format.
- Figures are supplied as editable PowerPoint (native Office format, one figure per slide) plus 600-dpi PNG, PDF, and TIFF.
- Tables are editable text in Word with horizontal rules only (no vertical rules, no shading), and are also supplied as a separate editable Word file.
- Numbered consecutively in Arabic numerals with captions supplied.

## Reproducibility

`build_submission.py` regenerates the whole package from the committed data, review, and results files. All reported counts, proportions, and confidence intervals are read from `results/`, `data/`, and `review/`; none are hard-coded. The manuscript citation numbering is written to `results/citation_order.json` so that the public `reproduce.py` renders the same reference numbers in the standalone editable tables.

## Sources

- Transport Economics and Management guide for authors: <https://www.sciencedirect.com/journal/transport-economics-and-management/publish/guide-for-authors> (read via the Web Archive copy of 2026 because the live page was blocked from the build environment)

The author should recheck the live submission-system item list, the article publishing charge, and the exact submission template immediately before upload.
