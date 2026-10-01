#!/usr/bin/env python3
"""Post hoc descriptive heterogeneity analyses added in response to peer review.

Reads the committed cross-sectional GBFS audit
(``data/gbfs_cross_sectional_audit.csv``) and the operator document sample
(``audit/operator_sample.csv``), and writes stratified descriptive summaries
to ``results/``:

* ``gbfs_geography.csv`` -- eligible motorized feeds by country with field
  prevalence and 95% Wilson CIs;
* ``gbfs_region_summary.csv`` -- the same at broad-region level;
* ``gbfs_version_summary.csv`` -- by declared GBFS version;
* ``gbfs_size_summary.csv`` -- by snapshot-vehicle-count quartile;
* ``gbfs_domain_heterogeneity.csv`` -- per operator website domain;
* ``gbfs_equal_domain_weight.csv`` -- equal-domain-weighted field prevalence;
* ``gbfs_clustering.csv`` -- systems-per-domain distribution and
  within-domain uniformity of each field;
* ``operator_markets.csv`` -- principal geographical markets of the sampled
  document-audit operators, derived from the countries in which that
  operator's audited GBFS systems are located;
* ``gbfs_heterogeneity_summary.md`` -- human-readable digest.

All statistics are descriptive (n/N, percentages, medians, IQRs). No
inferential testing is performed. Denominators are explicit in every row.
"""

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "data" / "gbfs_cross_sectional_audit.csv"
SAMPLE = ROOT / "audit" / "operator_sample.csv"
RESULTS = ROOT / "results"

FIELDS = [
    ("has_vehicle_id", "vehicle identifier"),
    ("has_location_fields", "latitude/longitude"),
    ("has_last_reported", "last-reported timestamp"),
    ("has_battery_percent", "battery/fuel percentage"),
    ("has_range", "current range"),
    ("has_deep_link", "vehicle-specific rental link"),
]

MICROMOBILITY_FORM_FACTORS = {
    "bicycle", "bike", "cargo_bicycle", "moped", "scooter", "scooter_standing",
}

# Broad-region grouping of every ISO-3166 alpha-2 code observed among the
# eligible motorized feeds (35 codes). Europe is kept as one region because
# sub-dividing it would leave strata too small to describe.
REGION = {
    # Europe
    "AT": "Europe", "BA": "Europe", "BE": "Europe", "CH": "Europe",
    "CY": "Europe", "CZ": "Europe", "DE": "Europe", "DK": "Europe",
    "ES": "Europe", "FI": "Europe", "FR": "Europe", "GB": "Europe",
    "GR": "Europe", "HR": "Europe", "HU": "Europe", "IE": "Europe",
    "IT": "Europe", "LI": "Europe", "NL": "Europe", "NO": "Europe",
    "PL": "Europe", "PT": "Europe", "RO": "Europe", "SE": "Europe",
    "SI": "Europe", "SK": "Europe", "UA": "Europe",
    # Northern America
    "CA": "Northern America", "US": "Northern America",
    # Oceania
    "NZ": "Oceania",
    # Western Asia
    "AE": "Western Asia", "IL": "Western Asia", "QA": "Western Asia",
    "SA": "Western Asia",
    # South-Eastern Asia
    "MY": "South-Eastern Asia",
}

COUNTRY_NAME = {
    "AE": "United Arab Emirates", "AT": "Austria", "BA": "Bosnia and Herzegovina",
    "BE": "Belgium", "CA": "Canada", "CH": "Switzerland", "CY": "Cyprus",
    "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark", "ES": "Spain",
    "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece",
    "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IL": "Israel",
    "IT": "Italy", "LI": "Liechtenstein", "MY": "Malaysia", "NL": "Netherlands",
    "NO": "Norway", "NZ": "New Zealand", "PL": "Poland", "PT": "Portugal",
    "QA": "Qatar", "RO": "Romania", "SA": "Saudi Arabia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "UA": "Ukraine", "US": "United States",
}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def form_factors(row: dict) -> set:
    return set(filter(None, row["form_factors"].split(";")))


def eligible_motorized(row: dict) -> bool:
    return (
        row["vehicle_status_status"] == "200"
        and row["vehicle_count"].isdigit()
        and int(row["vehicle_count"]) > 0
        and bool(form_factors(row) & MICROMOBILITY_FORM_FACTORS)
        and row["motorized_declared"] == "true"
    )


def field_row(dimension: str, level: str, field: str, label: str,
              k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {
        "dimension": dimension,
        "level": level,
        "metric": field,
        "label": label,
        "count": str(k),
        "denominator": str(n),
        "percent": f"{100 * k / n:.1f}" if n else "",
        "wilson_95_low_percent": f"{100 * lo:.1f}" if n else "",
        "wilson_95_high_percent": f"{100 * hi:.1f}" if n else "",
    }


def stratified(rows, keyfunc, dimension):
    groups = defaultdict(list)
    for r in rows:
        groups[keyfunc(r)].append(r)
    out = []
    for level, g in sorted(groups.items(),
                           key=lambda kv: (-len(kv[1]), str(kv[0]))):
        out.append({
            "dimension": dimension, "level": level, "metric": "feeds",
            "label": "Eligible motorized feeds",
            "count": str(len(g)), "denominator": str(len(rows)),
            "percent": f"{100 * len(g) / len(rows):.1f}" if rows else "",
            "wilson_95_low_percent": "", "wilson_95_high_percent": "",
        })
        for field, label in FIELDS:
            k = sum(r[field] == "true" for r in g)
            out.append(field_row(dimension, level, field, label, k, len(g)))
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def median_iqr(vals: list[float]) -> tuple[float, float, float]:
    s = sorted(vals)
    n = len(s)
    def pct(p):
        if n == 1:
            return s[0]
        pos = (n - 1) * p
        lo = int(pos)
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        return s[lo] + (s[hi] - s[lo]) * frac
    return pct(0.5), pct(0.25), pct(0.75)


def main() -> None:
    rows = list(csv.DictReader(AUDIT.open(encoding="utf-8")))
    motor = [r for r in rows if eligible_motorized(r)]
    n_motor = len(motor)

    # --- geography --------------------------------------------------------
    geo = stratified(motor, lambda r: f"{r['country_code']} {COUNTRY_NAME.get(r['country_code'], '')}".strip(), "country")
    region = stratified(motor, lambda r: REGION.get(r["country_code"], "Other"), "region")
    write_csv(RESULTS / "gbfs_geography.csv", geo)
    write_csv(RESULTS / "gbfs_region_summary.csv", region)

    # --- GBFS version -----------------------------------------------------
    def major_version(r):
        v = (r["declared_version"] or "").strip()
        if not v:
            return "not declared"
        return f"v{v.split('.')[0]}.x" if v[0].isdigit() else v
    version = stratified(motor, major_version, "gbfs_version")
    write_csv(RESULTS / "gbfs_version_summary.csv", version)

    # --- snapshot system size (vehicle_count quartiles) -------------------
    counts = sorted(int(r["vehicle_count"]) for r in motor)
    q = [counts[int((len(counts) - 1) * p)] for p in (0.25, 0.5, 0.75)]
    def size_band(r):
        v = int(r["vehicle_count"])
        for i, edge in enumerate(q):
            if v <= edge:
                return f"Q{i+1} (<= {edge} vehicles)"
        return f"Q4 (> {q[2]} vehicles)"
    size = stratified(motor, size_band, "snapshot_vehicle_count_quartile")
    size.insert(0, {
        "dimension": "snapshot_vehicle_count_quartile",
        "level": "distribution",
        "metric": "vehicle_count_summary",
        "label": "Snapshot vehicle count: median (IQR), range",
        "count": f"median {median_iqr(counts)[0]:.0f} "
                 f"(IQR {median_iqr(counts)[1]:.0f}-{median_iqr(counts)[2]:.0f}); "
                 f"range {min(counts)}-{max(counts)}",
        "denominator": str(n_motor), "percent": "",
        "wilson_95_low_percent": "", "wilson_95_high_percent": "",
    })
    write_csv(RESULTS / "gbfs_size_summary.csv", size)

    # --- operator-domain heterogeneity ------------------------------------
    by_domain = defaultdict(list)
    for r in motor:
        by_domain[r["website_domain"] or "(missing)"].append(r)
    dom_rows = []
    for domain, g in sorted(by_domain.items(),
                            key=lambda kv: (-len(kv[1]), kv[0])):
        row = {
            "website_domain": domain,
            "eligible_motorized_feeds": str(len(g)),
            "countries": ";".join(sorted({r["country_code"] for r in g})),
            "versions": ";".join(sorted({(r["declared_version"] or "?").strip() for r in g})),
        }
        for field, _ in FIELDS:
            k = sum(r[field] == "true" for r in g)
            row[f"{field}_n"] = str(k)
            row[f"{field}_pct"] = f"{100 * k / len(g):.1f}"
        dom_rows.append(row)
    write_csv(RESULTS / "gbfs_domain_heterogeneity.csv", dom_rows)

    # equal-domain weighting: mean of per-domain proportions
    eq_rows = []
    for field, label in FIELDS:
        props = [sum(r[field] == "true" for r in g) / len(g)
                 for g in by_domain.values()]
        med, q1, q3 = median_iqr(props)
        k_any = sum(any(r[field] == "true" for r in g) for g in by_domain.values())
        k_all = sum(all(r[field] == "true" for r in g) for g in by_domain.values())
        eq_rows.append({
            "metric": field, "label": label,
            "mean_domain_prevalence_pct": f"{100 * sum(props) / len(props):.1f}",
            "median_domain_prevalence_pct": f"{100 * med:.1f}",
            "iqr_domain_prevalence_pct": f"{100 * q1:.1f}-{100 * q3:.1f}",
            "domains_any": str(k_any), "domains_all": str(k_all),
            "n_domains": str(len(by_domain)),
        })
    write_csv(RESULTS / "gbfs_equal_domain_weight.csv", eq_rows)

    # clustering: systems per domain + within-domain uniformity
    sizes = [len(g) for g in by_domain.values()]
    smed, sq1, sq3 = median_iqr(sizes)
    cl_rows = [{
        "statistic": "domains_with_eligible_feeds", "value": str(len(by_domain)),
    }, {
        "statistic": "systems_per_domain_median",
        "value": f"{smed:.0f}",
    }, {
        "statistic": "systems_per_domain_iqr", "value": f"{sq1:.0f}-{sq3:.0f}",
    }, {
        "statistic": "systems_per_domain_range",
        "value": f"{min(sizes)}-{max(sizes)}",
    }, {
        "statistic": "largest_domain_share_pct",
        "value": f"{100 * max(sizes) / n_motor:.1f}",
    }, {
        "statistic": "top5_domain_share_pct",
        "value": f"{100 * sum(sorted(sizes, reverse=True)[:5]) / n_motor:.1f}",
    }]
    for field, label in FIELDS:
        multi = [g for g in by_domain.values() if len(g) >= 2]
        uniform = sum(1 for g in multi
                      if len({r[field] for r in g}) == 1)
        cl_rows.append({
            "statistic": f"uniform_{field}",
            "value": f"{uniform}/{len(multi)} multi-feed domains uniform",
        })
    write_csv(RESULTS / "gbfs_clustering.csv", cl_rows)

    # --- WP3 operator principal markets (data-derived) --------------------
    sample = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    market_rows = []
    for s in sample:
        dom = s["operator_domain"]
        sys_all = [r for r in rows if r["website_domain"] == dom]
        sys_motor = [r for r in motor if r["website_domain"] == dom]
        basis = sys_motor if sys_motor else sys_all
        countries = sorted({r["country_code"] for r in basis})
        regions = sorted({REGION.get(c, "Other") for c in countries})
        names = [COUNTRY_NAME.get(c, c) for c in countries]
        market_rows.append({
            "operator_domain": dom,
            "sample_rank": s["sample_rank"],
            "n_registry_systems": str(len(sys_all)),
            "n_eligible_motorized_feeds": str(len(sys_motor)),
            "market_basis": ("countries of eligible motorized feeds"
                             if sys_motor else
                             "countries of registry systems (no eligible "
                             "motorized feed at audit time)"),
            "n_countries": str(len(countries)),
            "countries": ";".join(names),
            "regions": ";".join(regions),
        })
    write_csv(RESULTS / "operator_markets.csv", market_rows)

    # --- digest -----------------------------------------------------------
    lines = [
        "# Post hoc heterogeneity analyses (added in response to peer review)",
        "",
        f"Eligible motorized feeds: {n_motor}; countries: "
        f"{len({r['country_code'] for r in motor})}; operator domains: "
        f"{len(by_domain)}.",
        "",
        "All values are descriptive: n/N, percentages with 95% Wilson CIs,",
        "medians/IQRs. No inferential testing was performed. 'Snapshot vehicle",
        "count' is the number of vehicles returned by the feed at collection",
        "time; it is not a measure of city population or total fleet size.",
        "",
        "## Systems per operator domain",
        f"median {smed:.0f} (IQR {sq1:.0f}-{sq3:.0f}), range "
        f"{min(sizes)}-{max(sizes)}; largest domain {max(sizes)} feeds "
        f"({100 * max(sizes) / n_motor:.1f}% of eligible feeds).",
        "",
        "## Top countries",
    ]
    for g in geo:
        if g["metric"] == "feeds":
            lines.append(f"- {g['level']}: {g['count']} ({g['percent']}%)")
    lines += ["", "## Equal-domain-weighted field prevalence"]
    for r in eq_rows:
        lines.append(
            f"- {r['label']}: mean {r['mean_domain_prevalence_pct']}% "
            f"(median {r['median_domain_prevalence_pct']}%, "
            f"IQR {r['iqr_domain_prevalence_pct']}); "
            f"{r['domains_any']}/{r['n_domains']} domains any feed, "
            f"{r['domains_all']}/{r['n_domains']} all feeds")
    (RESULTS / "gbfs_heterogeneity_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote heterogeneity outputs for {n_motor} eligible feeds, "
          f"{len(by_domain)} domains")


if __name__ == "__main__":
    main()
