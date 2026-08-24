# Research in Transportation Business & Management submission requirements checked on 24 August 2026

Target journal: **Research in Transportation Business & Management** (Elsevier), hybrid open access, double-anonymized peer review.

## Scope and article positioning

Research in Transportation Business & Management publishes research on international aspects of transport management, including business strategy, communication, sustainability, finance, human resource management, law, logistics, marketing, franchising, privatisation, and commercialisation. This manuscript is submitted as a **Research article**. It contributes:

1. a PRISMA-ScR evidence map of direct data-exposure evidence in shared micromobility;
2. a global, privacy-preserving audit of what public GBFS vehicle feeds actually disclose;
3. a structured audit of public operator lifecycle-disclosure documents; and
4. a reproducible lifecycle exposure model linking evidence strength to procurement, risk governance, and transparency choices.

## Format

- **Research article**, normally up to 8,000 words excluding references.
- **Abstract** of no more than 250 words, unstructured.
- **Highlights**: 3-5 bullets, each no more than 85 characters including spaces.
- **1-7 keywords**, separated by semicolons; avoid multi-word keywords containing "and" or "of".
- **APA author-date references**: in-text citations give author surname(s) and year (e.g. `(Elzer et al., 2025)` or `(Arksey & O'Malley, 2005)`); three or more authors use `et al.`; the reference list is alphabetised by first author and works by the same author are ordered chronologically. At submission, references may be in any consistent style as long as in-text citations follow APA.
- The manuscript is **anonymized** (RTBM uses double-anonymized peer review); author details are supplied only on the separate title page and cover letter.

## Required disclosure statements

Placed after the main text and before the references:

- **Data availability statement** (required) — states where the registry snapshot, screening decisions, coding sheets, results, and code are available to reviewers, and the restrictions on raw identifiers/coordinates;
- **Funding statement** (required);
- **Competing interests** (required).

Additionally supplied as good practice: acknowledgements, author contributions, an ethical-standards statement, and a generative-AI use statement.

## Figures and tables

- Five figures and five tables, each cited in the body before or at first appearance and placed immediately after that paragraph.
- Figures are supplied separately as editable PowerPoint, plus 600-dpi PNG, PDF, and TIFF; tables are supplied in a separate editable Word file.
- Numbered consecutively in Arabic numerals with captions supplied.

## Reproducibility

`build_submission.py` regenerates the whole package from the committed data, review, and results files. All reported counts, proportions, and confidence intervals are read from `results/`, `data/`, and `review/`; none are hard-coded. Source files are not required at initial submission but are retained and can be supplied if accepted.

## Sources

- Research in Transportation Business & Management guide for authors: <https://www.sciencedirect.com/journal/research-in-transportation-business-and-management/publish/guide-for-authors>
- APA style reference examples: <https://apastyle.apa.org/style-grammar-guidelines/references/examples>

The author should recheck the live submission-system item list and the exact RTBM template immediately before upload.
