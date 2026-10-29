#!/usr/bin/env python3

import argparse
import csv
from collections import Counter
from pathlib import Path


TITLE_DECISIONS = {"", "include", "exclude", "uncertain"}
FULL_TEXT_STATUSES = {"not_sought", "retrieved", "not_retrieved"}
FULL_TEXT_DECISIONS = {"", "include", "exclude", "uncertain"}
EVIDENCE_DISTANCES = {"", "D4", "D3", "D2", "D1", "N"}
TITLE_REASONS = {
    "",
    "E1_WRONG_DOMAIN",
    "E2_WRONG_TOPIC",
    "E3_NO_EVIDENCE",
    "E4_DUPLICATE",
    "E5_DATE_LANGUAGE",
    "E6_UNVERIFIABLE",
}
FULL_TEXT_REASONS = {
    "",
    "F1_NO_RELEVANT_DATA_PATH",
    "F2_MECHANISM_NOT_TRANSFERABLE",
    "F3_SECONDARY_WITHOUT_ADDED_SYNTHESIS",
    "F4_NOT_RETRIEVED",
    "F5_SUPERSEDED",
    "F6_UNSAFE_DETAIL_ONLY",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate manual screening decisions.")
    parser.add_argument("--screening", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    with args.screening.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    errors: list[str] = []
    seen_ids: set[str] = set()
    for line_number, row in enumerate(rows, start=2):
        record_id = row.get("record_id", "")
        if not record_id:
            errors.append(f"line {line_number}: missing record_id")
        elif record_id in seen_ids:
            errors.append(f"line {line_number}: duplicate record_id {record_id}")
        seen_ids.add(record_id)
        title_decision = row.get("title_abstract_decision", "")
        title_reason = row.get("title_abstract_reason", "")
        full_status = row.get("full_text_status", "")
        full_decision = row.get("full_text_decision", "")
        full_reason = row.get("full_text_exclusion_reason", "")
        distance = row.get("evidence_distance", "")
        if title_decision not in TITLE_DECISIONS:
            errors.append(f"line {line_number}: invalid title decision {title_decision}")
        if title_reason not in TITLE_REASONS:
            errors.append(f"line {line_number}: invalid title reason {title_reason}")
        if title_decision == "exclude" and not title_reason:
            errors.append(f"line {line_number}: title exclusion requires a reason")
        if full_status not in FULL_TEXT_STATUSES:
            errors.append(f"line {line_number}: invalid full-text status {full_status}")
        if full_decision not in FULL_TEXT_DECISIONS:
            errors.append(f"line {line_number}: invalid full-text decision {full_decision}")
        if full_reason not in FULL_TEXT_REASONS:
            errors.append(f"line {line_number}: invalid full-text reason {full_reason}")
        if full_decision == "exclude" and not full_reason:
            errors.append(f"line {line_number}: full-text exclusion requires a reason")
        if distance not in EVIDENCE_DISTANCES:
            errors.append(f"line {line_number}: invalid evidence distance {distance}")
        if full_decision == "include" and not distance:
            errors.append(f"line {line_number}: included record requires evidence distance")
    if errors:
        raise RuntimeError("\n".join(errors[:100]))
    title_counts = Counter(row["title_abstract_decision"] or "pending" for row in rows)
    full_counts = Counter(row["full_text_decision"] or "pending" for row in rows)
    print(f"Validated {len(rows)} records")
    print(f"Title/abstract decisions: {dict(title_counts)}")
    print(f"Full-text decisions: {dict(full_counts)}")


if __name__ == "__main__":
    main()
