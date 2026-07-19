# Data & Policy submission requirements checked on 15 July 2026

Target journal: **Data & Policy** (Cambridge University Press), an open-access
journal on the interface of data science and governance. After desk rejection
by *Computers & Security* (scope mismatch), the package was reformatted for
Data & Policy; the next fallback target is *International Journal of Information
Security*.

## Scope and article positioning

Data & Policy publishes research at the intersection of data (including data
science, digital technologies, and open data) and its use, regulation, and
governance. This manuscript is submitted as a **Research Article** under
**Area 4: Ethics, Equity and Trustworthiness of Data**. It contributes:

1. a PRISMA-ScR evidence map of direct data-exposure evidence in shared
   micromobility;
2. a global, privacy-preserving audit of what public GBFS vehicle feeds
   actually disclose;
3. a structured audit of public operator lifecycle-disclosure documents; and
4. a reproducible lifecycle exposure model linking evidence strength to
   procurement, regulatory, and transparency choices.

## Format

- **Research Article**, approximately 8,000 words excluding references (a
  guideline, not a hard limit); the current main text is well within this.
- **Abstract** of no more than 250 words.
- A **Policy Significance Statement** of ~120 words, in accessible language,
  placed directly beneath the abstract.
- Up to **five keywords**, separated by semicolons.
- **Cambridge A (author-date) references**: in-text citations give author
  surname and year with no intervening punctuation (e.g. `(Elzer et al. 2025)`);
  three or more authors use `et al.`; multiple works are separated by
  semicolons and ordered alphabetically by author; the reference list is
  alphabetised (not numbered) and works by the same author are ordered
  chronologically.
- The manuscript is **not anonymized** (Data & Policy uses single-blind peer
  review); a title/author page with ORCID is supplied.

## Required disclosure statements

Placed after the main text and before the references:

- **Data availability statement** (required) — states where the registry
  snapshot, screening decisions, coding sheets, results, and code are openly
  available, and the restrictions on raw identifiers/coordinates;
- **Funding statement** (required);
- **Competing interests** (required).

Additionally supplied as good practice: acknowledgements, author contributions,
an ethical-standards statement, and a generative-AI use statement.

## Figures and tables

- Five figures and five tables, each cited in the body before or at first
  appearance and placed immediately after that paragraph.
- Figures are also supplied separately as editable PowerPoint, plus 600-dpi
  PNG, PDF, and TIFF; tables are supplied in a separate editable Word file.
- Numbered consecutively in Arabic numerals with captions supplied.
- Accessibility descriptions/alt text should be provided at the publication
  stage.

## Reproducibility

`build_submission.py` regenerates the whole package from the committed data,
review, and results files. All reported counts, proportions, and confidence
intervals are read from `results/`, `data/`, and `review/`; none are
hard-coded. Source files are not required at initial submission but are
retained and can be supplied if accepted.

## Sources

- Data & Policy information for authors:
  <https://www.cambridge.org/core/journals/data-and-policy/information/instructions-contributors>
- Cambridge author-date (Cambridge A) reference style guidance (via the
  journal's instructions for contributors).

The author should recheck the live submission-system item list and the exact
Cambridge template immediately before upload.
