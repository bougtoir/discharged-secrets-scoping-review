#!/usr/bin/env python3

import argparse
import csv
import hashlib
import re
import unicodedata
from pathlib import Path


TARGET_TERMS = {
    "e-scooter",
    "electric scooter",
    "micromobility",
    "micro-mobility",
    "bike share",
    "bikeshare",
    "shared bicycle",
    "gbfs",
    "general bikeshare feed specification",
}
SECURITY_TERMS = {
    "security",
    "privacy",
    "cybersecurity",
    "attack",
    "vulnerability",
    "tracking",
    "telemetry",
    "forensic",
    "data leak",
    "spoofing",
    "re-identification",
    "reidentification",
}
NEAR_DOMAIN_TERMS = {
    "battery",
    "bms",
    "electric vehicle",
    "connected vehicle",
    "embedded system",
    "data remanence",
    "maintenance",
    "disposal",
    "second life",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a deterministic manual-screening table."
    )
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--seeds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def normalized_doi(value: str) -> str:
    doi = value.strip().lower()
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)


def normalized_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).lower()
    return re.sub(r"[^a-z0-9]+", "", normalized)


def record_id(title: str, doi: str) -> str:
    source = f"doi:{normalized_doi(doi)}" if doi else f"title:{normalized_title(title)}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]


def priority_tier(title: str, seed: bool) -> str:
    if seed:
        return "P1_SEED"
    text = title.lower()
    target = any(term in text for term in TARGET_TERMS)
    security = any(term in text for term in SECURITY_TERMS)
    near_domain = any(term in text for term in NEAR_DOMAIN_TERMS)
    if target and security:
        return "P1_DIRECT"
    if target:
        return "P2_TARGET"
    if security and near_domain:
        return "P2_NEAR_DOMAIN"
    if security or near_domain:
        return "P3_POSSIBLE"
    return "P4_LOW_SIGNAL"


def main() -> None:
    args = parse_args()
    with args.seeds.open(newline="", encoding="utf-8") as handle:
        seed_rows = list(csv.DictReader(handle))
    seed_dois = {
        normalized_doi(row.get("doi", ""))
        for row in seed_rows
        if row.get("doi")
    }
    seed_titles = {
        normalized_title(row.get("title", ""))
        for row in seed_rows
        if row.get("title")
    }
    with args.candidates.open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))

    rows: list[dict[str, str]] = []
    for candidate in candidates:
        doi = normalized_doi(candidate.get("doi", ""))
        title = candidate.get("title", "")
        is_seed = doi in seed_dois or normalized_title(title) in seed_titles
        rows.append(
            {
                "record_id": record_id(title, doi),
                "priority_tier": priority_tier(title, is_seed),
                "seed_record": str(is_seed).lower(),
                "title": title,
                "year": candidate.get("year", ""),
                "doi": doi,
                "url": candidate.get("url", ""),
                "venue": candidate.get("venue", ""),
                "query_ids": candidate.get("query_ids", ""),
                "source_apis": candidate.get("source_apis", ""),
                "title_abstract_decision": "",
                "title_abstract_reason": "",
                "full_text_status": "not_sought",
                "full_text_decision": "",
                "full_text_exclusion_reason": "",
                "evidence_distance": "",
                "reviewer_note": "",
                "first_pass_date": "",
                "second_pass_date": "",
                "second_pass_decision": "",
                "resolution": "",
            }
        )
    priority_order = {
        "P1_SEED": 0,
        "P1_DIRECT": 1,
        "P2_TARGET": 2,
        "P2_NEAR_DOMAIN": 3,
        "P3_POSSIBLE": 4,
        "P4_LOW_SIGNAL": 5,
    }
    rows.sort(
        key=lambda row: (
            priority_order[row["priority_tier"]],
            -(int(row["year"]) if row["year"].isdigit() else 0),
            row["title"].lower(),
        )
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Initialized {len(rows)} screening records")
    print(f"Seed records matched: {sum(row['seed_record'] == 'true' for row in rows)}")


if __name__ == "__main__":
    main()
