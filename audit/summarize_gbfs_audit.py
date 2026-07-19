#!/usr/bin/env python3

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


FIELDS = [
    ("has_vehicle_id", "Vehicle identifier"),
    ("has_location_fields", "Latitude and longitude"),
    ("has_last_reported", "Last-reported timestamp"),
    ("has_battery_percent", "Battery or fuel percentage"),
    ("has_range", "Current range"),
    ("has_deep_link", "Vehicle-specific rental URI"),
]
MICROMOBILITY_FORM_FACTORS = {
    "bicycle",
    "bike",
    "cargo_bicycle",
    "moped",
    "scooter",
    "scooter_standing",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize aggregate GBFS audit results.")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--summary-csv", type=Path, required=True)
    parser.add_argument("--operator-csv", type=Path, required=True)
    parser.add_argument("--summary-md", type=Path, required=True)
    return parser.parse_args()


def integer(value: str) -> int:
    return int(value) if value.isdigit() else 0


def wilson(successes: int, total: int) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    return centre - half_width, centre + half_width


def metric_row(
    stratum: str,
    metric: str,
    label: str,
    successes: int,
    total: int,
) -> dict[str, str]:
    low, high = wilson(successes, total)
    return {
        "stratum": stratum,
        "metric": metric,
        "label": label,
        "count": str(successes),
        "denominator": str(total),
        "percent": f"{100 * successes / total:.2f}" if total else "",
        "wilson_95_low_percent": f"{100 * low:.2f}" if total else "",
        "wilson_95_high_percent": f"{100 * high:.2f}" if total else "",
    }


def form_factors(row: dict[str, str]) -> set[str]:
    return set(filter(None, row["form_factors"].split(";")))


def declared_micromobility(row: dict[str, str]) -> bool:
    return bool(form_factors(row) & MICROMOBILITY_FORM_FACTORS)


def declared_motorized_micromobility(row: dict[str, str]) -> bool:
    return declared_micromobility(row) and row["motorized_declared"] == "true"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    with args.audit.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    reachable = [row for row in rows if row["auto_discovery_status"] == "200"]
    vehicle_feed = [row for row in rows if row["has_vehicle_status"] == "true"]
    successful_vehicle_feed = [
        row for row in vehicle_feed if row["vehicle_status_status"] == "200"
    ]
    evaluable = [
        row
        for row in successful_vehicle_feed
        if integer(row["vehicle_count"]) > 0
    ]
    summary = [
        metric_row(
            "all_registry_entries",
            "auto_discovery_reachable",
            "Reachable auto-discovery endpoint",
            len(reachable),
            len(rows),
        ),
        metric_row(
            "reachable_registry_entries",
            "vehicle_feed_declared",
            "Vehicle-status feed declared",
            len(vehicle_feed),
            len(reachable),
        ),
        metric_row(
            "declared_vehicle_feeds",
            "vehicle_feed_successful",
            "Vehicle-status feed successfully retrieved",
            len(successful_vehicle_feed),
            len(vehicle_feed),
        ),
        metric_row(
            "successful_vehicle_feeds",
            "vehicle_feed_nonempty",
            "Successfully retrieved feed with at least one vehicle",
            len(evaluable),
            len(successful_vehicle_feed),
        ),
        metric_row(
            "reachable_registry_entries",
            "motorized_declared",
            "At least one non-human propulsion type declared",
            sum(row["motorized_declared"] == "true" for row in reachable),
            len(reachable),
        ),
    ]
    strata = [
        ("all_evaluable_vehicle_feeds", evaluable),
        (
            "declared_micromobility_feeds",
            [row for row in evaluable if declared_micromobility(row)],
        ),
        (
            "declared_motorized_micromobility_feeds",
            [row for row in evaluable if declared_motorized_micromobility(row)],
        ),
    ]
    for stratum, stratum_rows in strata:
        for field, label in FIELDS:
            summary.append(
                metric_row(
                    stratum,
                    field,
                    label,
                    sum(row[field] == "true" for row in stratum_rows),
                    len(stratum_rows),
                )
            )
    motorized_micro_rows = strata[-1][1]
    operator_motorized_micro: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in motorized_micro_rows:
        operator_motorized_micro[row["website_domain"] or "(missing)"].append(row)
    for field, label in FIELDS:
        summary.append(
            metric_row(
                "declared_motorized_micromobility_operator_domains_any",
                field,
                f"{label} in at least one eligible feed",
                sum(
                    any(row[field] == "true" for row in operator_rows)
                    for operator_rows in operator_motorized_micro.values()
                ),
                len(operator_motorized_micro),
            )
        )
        summary.append(
            metric_row(
                "declared_motorized_micromobility_operator_domains_all",
                field,
                f"{label} in every eligible feed",
                sum(
                    all(row[field] == "true" for row in operator_rows)
                    for operator_rows in operator_motorized_micro.values()
                ),
                len(operator_motorized_micro),
            )
        )
    write_csv(args.summary_csv, summary)

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["website_domain"] or "(missing)"].append(row)
    operator_rows: list[dict[str, str]] = []
    for operator, operator_systems in grouped.items():
        operator_evaluable = [
            row
            for row in operator_systems
            if row["vehicle_status_status"] == "200"
            and integer(row["vehicle_count"]) > 0
        ]
        operator_rows.append(
            {
                "website_domain": operator,
                "registry_systems": str(len(operator_systems)),
                "reachable_systems": str(
                    sum(row["auto_discovery_status"] == "200" for row in operator_systems)
                ),
                "motorized_declared_systems": str(
                    sum(row["motorized_declared"] == "true" for row in operator_systems)
                ),
                "motorized_micromobility_systems": str(
                    sum(
                        declared_motorized_micromobility(row)
                        for row in operator_systems
                    )
                ),
                "evaluable_vehicle_feeds": str(len(operator_evaluable)),
                "battery_percent_feeds": str(
                    sum(row["has_battery_percent"] == "true" for row in operator_evaluable)
                ),
                "range_feeds": str(
                    sum(row["has_range"] == "true" for row in operator_evaluable)
                ),
                "last_reported_feeds": str(
                    sum(row["has_last_reported"] == "true" for row in operator_evaluable)
                ),
            }
        )
    operator_rows.sort(
        key=lambda row: (
            -int(row["motorized_micromobility_systems"]),
            row["website_domain"],
        )
    )
    write_csv(args.operator_csv, operator_rows)

    lines = [
        "# Preliminary GBFS cross-sectional audit",
        "",
        "These results describe public-feed availability and field presence at the recorded collection time. They do not establish backend collection, identifier rotation, trip reconstruction, operator intent, or security compliance.",
        "",
        "| Stratum | Metric | Count / denominator | Percent (95% Wilson CI) |",
        "|---|---|---:|---:|",
    ]
    for row in summary:
        percent = (
            f"{row['percent']}% ({row['wilson_95_low_percent']}–"
            f"{row['wilson_95_high_percent']}%)"
            if row["percent"]
            else "not estimable"
        )
        lines.append(
            f"| {row['stratum']} | {row['label']} | "
            f"{row['count']} / {row['denominator']} | {percent} |"
        )
    lines.extend(
        [
            "",
            "Field-presence denominators include only successfully retrieved, non-empty vehicle-status feeds. Empty feeds are not treated as evidence that a field is unsupported.",
        ]
    )
    args.summary_md.parent.mkdir(parents=True, exist_ok=True)
    args.summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(summary)} aggregate metrics")
    print(f"Wrote {len(operator_rows)} operator-domain rows")


if __name__ == "__main__":
    main()
