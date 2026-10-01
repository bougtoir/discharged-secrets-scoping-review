#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select the prespecified primary operator-document sample."
    )
    parser.add_argument("--operator-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.operator_summary.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    eligible = [
        row
        for row in rows
        if int(row["motorized_micromobility_systems"]) > 0
    ]
    eligible.sort(
        key=lambda row: (
            -int(row["motorized_micromobility_systems"]),
            row["website_domain"],
        )
    )
    selected = eligible[: args.size]
    output_rows = [
        {
            "sample_rank": str(index),
            "operator_domain": row["website_domain"],
            "motorized_micromobility_systems": row[
                "motorized_micromobility_systems"
            ],
            "registry_systems": row["registry_systems"],
            "selection_rule": "top domains by declared motorized micromobility systems",
        }
        for index, row in enumerate(selected, start=1)
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(output_rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Selected {len(output_rows)} operator domains")


if __name__ == "__main__":
    main()
