#!/usr/bin/env python3
"""Computer-assisted single-reviewer coding of public operator privacy policies.

For each operator-document pair the script searches the locally cached document
text for domain-specific expressions, assigns a codebook status, and records the
matching sentence as a verifiable locator quotation. Coding is deterministic and
reproducible; the reviewer inspected the emitted quotations and adjusted the
status overrides below where the automated match was misleading.

Only short quotations (verification locators) are written to the committed CSV.
The full document text is never committed.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT.parent / "review" / ".doc_cache"
OUT = ROOT.parent / "data" / "document_audit.csv"

# Operator-document rows in the audit sample. jurisdiction reflects the
# retrieved version. status "coded" documents are read; "unavailable" documents
# could not be retrieved as machine-readable text via a reproducible request.
OPERATORS = [
    ("Dott (TIER-Dott)", "EU", "dott-privacy-policy", "coded"),
    ("Bird", "Global", "bird-privacy-policy", "coded"),
    ("Lime", "Global", "lime-privacy-notice", "coded"),
    ("Bolt", "Global", "bolt-global-privacy-notice-for-passengers", "coded"),
    ("Donkey Republic", "EU", "donkey-republic-privacy-policy", "coded"),
    ("Beryl", "UK", "beryl-privacy-notice", "coded"),
    ("Zeus Scooters", "EU", "zeus-scooters-privacy-policy", "coded"),
    ("Veo", "US", "veo-veo-privacy-policy", "coded"),
    ("Spin", "US", "spin-privacy-policy", "coded"),
    ("Check", "EU", "check-privacy-statement", "coded"),
    ("nextbike", "DE", "nextbike-privacy-notice-nextbike-app", "coded"),
    ("nextbike Czech Republic", "CZ", "nextbike-czech-republic-data-privacy-policy", "coded"),
    ("Cooltra", "EU", "cooltra-privacy-policy", "coded"),
    ("Voi", "UK", "voi-privacy-policy", "unavailable"),
    ("Mobility Parc", "EU", "mobility-parc-service-website-with-personal-data-policy-link", "unavailable"),
]

DOMAINS = [
    ("location_data", [r"geolocation", r"\bgps\b", r"location data", r"your location", r"location of (your|the) (device|vehicle)"], [r"\blocation\b"]),
    ("trip_time_data", [r"trip", r"route(s)? taken", r"journey", r"start and (end|destination)", r"ride (history|and geolocation)", r"duration", r"timestamp", r"rental (status|transactions?)", r"beginning and end of the rental"], [r"\bride\b"]),
    ("vehicle_identifier", [r"vehicle identifier", r"vehicle id\b", r"device identifier", r"\bimei\b", r"unique identifier", r"persistent identifier", r"device token"], [r"identifier"]),
    ("battery_or_diagnostic_data", [r"battery", r"telemetry", r"diagnostic", r"state of charge", r"braking", r"speed"], [r"vehicle data"]),
    ("maintenance_or_repair_data", [r"maintenance", r"repair", r"fault", r"malfunction", r"customer (service|support)"], [r"support"]),
    ("account_payment_device_data", [r"payment", r"account", r"credit card", r"device information", r"\bip address\b"], [r"account"]),
    ("analytics_or_profiling", [r"analytics", r"profiling", r"automated (decision|processing)", r"fraud (detection|prevention)", r"advertis", r"targeted"], [r"cookies"]),
    ("retention", [r"retention", r"retain", r"how long we (keep|store)", r"storage period", r"kept for", r"no longer necessary"], [r"delete .* no longer"]),
    ("processors_or_contractors", [r"processor", r"sub-?processor", r"service provider", r"contractor", r"third(-| )part(y|ies)"], [r"share"]),
    ("international_transfer", [r"international transfer", r"outside the (eea|european|uk|united)", r"standard contractual clauses", r"adequacy", r"transfer(red)? .* (country|countries|outside)", r"stored .* (usa|united states)"], [r"transfer"]),
    ("user_rights", [r"right to (access|erasure|rectification|object|portability|delete)", r"right of access", r"data subject rights", r"deletion of your", r"correct or update"], [r"your rights"]),
    ("incident_contact", [r"data breach", r"security incident", r"notify", r"supervisory authority", r"data protection officer", r"\bdpo\b", r"lodge a complaint"], [r"contact us"]),
    ("vulnerability_disclosure", [r"vulnerability", r"responsible disclosure", r"security researcher", r"report a (security|vulnerability)", r"bug bounty"], []),
    ("return_recycling_disposal", [r"recycl", r"disposal", r"dispose", r"end.of.life", r"resale", r"refurbish", r"second.life"], []),
]

STATUS_OVERRIDE: dict[tuple[str, str], tuple[str, str]] = {}


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", flat) if len(s.strip()) > 20]


def first_match(sents: list[str], patterns: list[str]) -> str:
    for pat in patterns:
        rx = re.compile(pat, re.I)
        for s in sents:
            if rx.search(s):
                return s
    return ""


def main() -> None:
    fieldnames = [
        "operator_name", "jurisdiction", "document_status", "domain",
        "status", "quotation_or_locator",
    ]
    rows = []
    tallies: dict[str, dict[str, int]] = {d[0]: {} for d in DOMAINS}
    for name, juris, slug, docstatus in OPERATORS:
        path = CACHE / f"{slug}.txt"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        sents = sentences(text)
        for domain, strong, broad in DOMAINS:
            if docstatus == "unavailable" or not sents:
                status, quote = "unavailable", ""
            else:
                hit = first_match(sents, strong)
                if hit:
                    status, quote = "explicit", hit[:300]
                else:
                    hit = first_match(sents, broad)
                    status, quote = ("partial", hit[:300]) if hit else ("not_found", "")
            status, quote = STATUS_OVERRIDE.get((name, domain), (status, quote))
            tallies[domain][status] = tallies[domain].get(status, 0) + 1
            rows.append({
                "operator_name": name, "jurisdiction": juris,
                "document_status": docstatus, "domain": domain,
                "status": status, "quotation_or_locator": quote,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    coded = sum(1 for o in OPERATORS if o[3] == "coded")
    print(f"wrote {len(rows)} coded cells for {len(OPERATORS)} operators "
          f"({coded} coded, {len(OPERATORS) - coded} unavailable)")
    for domain, counts in tallies.items():
        print(f"  {domain:32} {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    main()
