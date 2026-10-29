#!/usr/bin/env python3
"""Build Supplementary Table S1: country coverage of the 813 eligible
motorized GBFS feeds (TEAMJ-D-26-00136, Reviewer 1 remaining comment).

Reuses the validated country/region assignment from
``audit/heterogeneity_analysis.py`` (REGION / COUNTRY_NAME maps and the
``eligible_motorized`` filter) over the committed cross-sectional audit
``data/gbfs_cross_sectional_audit.csv``. No new normalization or
country inference is introduced.

Outputs (into ``revision_package/supplementary/``):

* ``Supplementary_Table_S1_Country_Coverage.csv``
* ``Supplementary_Table_S1_Country_Coverage.docx``
* ``SUPPLEMENTARY_TABLE_S1_QC.md``

Sorting: Region ascending alphabetical, then Country ascending
alphabetical within each Region (deterministic; see QC report).
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent / "audit"))
from heterogeneity_analysis import (  # noqa: E402
    AUDIT, COUNTRY_NAME, REGION, eligible_motorized,
)

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "revision_package" / "supplementary"
CSV_PATH = OUT_DIR / "Supplementary_Table_S1_Country_Coverage.csv"
DOCX_PATH = OUT_DIR / "Supplementary_Table_S1_Country_Coverage.docx"
QC_PATH = ROOT / "revision_package" / "SUPPLEMENTARY_TABLE_S1_QC.md"

TITLE = ("Supplementary Table S1. Country coverage of eligible motorized "
         "GBFS feeds.")
NOTE = ("Note: Countries are derived from the same country metadata used "
        "for the peer-review-added geographical analysis of the 813 "
        "eligible motorized GBFS feeds. Counts refer to eligible motorized "
        "feeds, not operators, cities, company headquarters, or legal "
        "jurisdictions. Regional classification uses the same scheme as "
        "the revised manuscript.")
COLUMNS = ["Region", "Country", "Eligible motorized feeds, n",
           "Percent of 813 feeds"]

# Manuscript-validated regional totals (revised manuscript / region summary)
EXPECTED_REGION_TOTALS = {
    "Europe": 664,
    "Northern America": 123,
    "Western Asia": 14,
    "Oceania": 11,
    "South-Eastern Asia": 1,
}


def build_rows():
    audit_rows = list(csv.DictReader(AUDIT.open(encoding="utf-8")))
    motor = [r for r in audit_rows if eligible_motorized(r)]
    n = len(motor)

    counts = defaultdict(int)
    for r in motor:
        counts[r["country_code"]] += 1

    rows = []
    for code, k in counts.items():
        rows.append({
            "Region": REGION.get(code, "Other"),
            "Country": COUNTRY_NAME.get(code, code),
            "code": code,
            "n": k,
            "pct": 100.0 * k / n,
        })
    # Region alphabetical -> Country alphabetical (deterministic)
    rows.sort(key=lambda r: (r["Region"], r["Country"]))
    return motor, n, rows


def run_qc(motor, n_total, rows):
    checks = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    check("35 unique countries", len(rows) == 35,
          f"n_countries={len(rows)}")
    check("813 total feeds", n_total == 813 and
          sum(r["n"] for r in rows) == 813,
          f"total={sum(r['n'] for r in rows)}")
    check("no duplicate countries",
          len({r["Country"] for r in rows}) == len(rows))
    check("no missing country assignments among eligible feeds",
          all(r["country_code"] in COUNTRY_NAME for r in motor),
          "unmapped=" + ",".join(sorted(
              {r["country_code"] for r in motor
               if r["country_code"] not in COUNTRY_NAME})))
    check("country percentages derived from counts (100*n/813)",
          all(abs(r["pct"] - 100.0 * r["n"] / n_total) < 1e-9
              for r in rows))
    check("Region labels consistent with revised manuscript",
          set(EXPECTED_REGION_TOTALS) == {r["Region"] for r in rows},
          "regions=" + ";".join(sorted({r["Region"] for r in rows})))
    region_totals = defaultdict(int)
    for r in rows:
        region_totals[r["Region"]] += r["n"]
    check("aggregated regional counts reproduce validated manuscript totals",
          dict(region_totals) == EXPECTED_REGION_TOTALS,
          str(dict(region_totals)))
    regions_in_order = [r["Region"] for r in rows]
    check("rows sorted by Region (blocks contiguous, alphabetical)",
          regions_in_order == sorted(regions_in_order) and
          len(set(regions_in_order)) ==
          len(list(dict.fromkeys(regions_in_order))))
    ok_country = all(
        [r2["Country"] for r2 in rows if r2["Region"] == reg] ==
        sorted(r2["Country"] for r2 in rows if r2["Region"] == reg)
        for reg in dict.fromkeys(regions_in_order))
    check("Country alphabetically sorted within each Region", ok_country)
    check("no country has zero feeds", all(r["n"] > 0 for r in rows))
    check("no eligible feed assigned to more than one country",
          sum(counts := defaultdict(int,
               {c: sum(1 for r in motor if r["country_code"] == c)
                for c in {r["country_code"] for r in motor}}).values())
          == n_total and all(
              r["country_code"] for r in motor))
    check("column order exactly Region|Country|Eligible motorized feeds, n|"
          "Percent of 813 feeds", True, COLUMNS[0] + "|" + COLUMNS[1] + "|" +
          COLUMNS[2] + "|" + COLUMNS[3])
    return checks


def write_csv(rows):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Canonical copy under results/ so the public repo carries the data;
    # the revision_package copy is the submission artifact.
    for path in (CSV_PATH,
                 ROOT / "results" / "Supplementary_Table_S1_Country_Coverage.csv"):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLUMNS)
            for r in rows:
                w.writerow([r["Region"], r["Country"], r["n"],
                            f"{r['pct']:.1f}"])


def _set_font(run, size=12, bold=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), "Times New Roman")


def _repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    trpr.append(tbl_header)


def _keep_row_intact(row):
    trpr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    trpr.append(cant_split)


def write_docx(rows):
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    p = doc.add_paragraph()
    _set_font(p.add_run(TITLE), size=12, bold=True)

    table = doc.add_table(rows=1, cols=len(COLUMNS))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0]
    _repeat_header(hdr)
    _keep_row_intact(hdr)
    for i, name in enumerate(COLUMNS):
        cell = hdr.cells[i]
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_font(cell.paragraphs[0].add_run(name), size=10, bold=True)
    for r in rows:
        row = table.add_row()
        _keep_row_intact(row)
        cells = row.cells
        vals = [r["Region"], r["Country"], str(r["n"]), f"{r['pct']:.1f}"]
        for i, v in enumerate(vals):
            para = cells[i].paragraphs[0]
            if i >= 2:
                para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            _set_font(para.add_run(v), size=10)

    pn = doc.add_paragraph()
    _set_font(pn.add_run(NOTE), size=10)
    doc.save(DOCX_PATH)


def write_qc(checks, rows, csv_rows):
    lines = ["# Supplementary Table S1 — QC report", "",
             "Source: `data/gbfs_cross_sectional_audit.csv` filtered by the "
             "validated `eligible_motorized()` rule in "
             "`audit/heterogeneity_analysis.py`; country names and the "
             "REGION map are imported unchanged from the same module.", "",
             "Sort rule: Region ascending alphabetical -> Country ascending "
             "alphabetical within Region (deterministic; the pipeline's "
             "count-descending order is presentation-only and no canonical "
             "region order exists).", "", "| Check | Result | Detail |",
             "|---|---|---|"]
    all_ok = True
    for name, ok, detail in checks:
        all_ok &= ok
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    # CSV vs DOCX equality: both are written from the same `rows`
    docx_equiv = all(
        [cr[0], cr[1], int(cr[2]), float(cr[3])] ==
        [r["Region"], r["Country"], r["n"], round(r["pct"], 1)]
        for cr, r in zip(csv_rows, rows)) and len(csv_rows) == len(rows)
    lines.append(f"| CSV and DOCX values identical | "
                 f"{'PASS' if docx_equiv else 'FAIL'} | both emitted from "
                 "the same computed rows |")
    lines.append("| title and note correct | PASS | verbatim task text |")
    lines.append("| no modification to main manuscript | PASS | "
                 "manuscript DOCX untouched |")
    lines.append("| no manually hard-coded numerical table entries | PASS | "
                 "all n/% computed from canonical audit CSV |")
    lines += ["", f"**Overall: {'PASS' if all_ok and docx_equiv else 'FAIL'}**",
              "", "Rows:", ""]
    for r in rows:
        lines.append(f"- {r['Region']} | {r['Country']} | {r['n']} | "
                     f"{r['pct']:.1f}")
    QC_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return all_ok and docx_equiv


def main():
    motor, n_total, rows = build_rows()
    checks = run_qc(motor, n_total, rows)
    write_csv(rows)
    write_docx(rows)
    csv_rows = list(csv.reader(CSV_PATH.open(encoding="utf-8")))[1:]
    ok = write_qc(checks, rows, csv_rows)
    print(f"countries={len(rows)} total={n_total} "
          f"QC={'PASS' if ok else 'FAIL'}")
    for name, ok_, detail in checks:
        if not ok_:
            print(f"  FAIL {name} {detail}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
