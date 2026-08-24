#!/usr/bin/env python3
"""Reproducible single-reviewer title/abstract and full-text screening.

The screening is rule-based and deterministic so that a third party can
regenerate identical decisions from the frozen candidate corpus and the
OpenAlex abstract cache. Every decision is paired with a coded reason drawn
from the protocol's exclusion taxonomy. Single-reviewer screening remains an
explicit limitation; a delayed 20% re-screen pass is recorded for consistency.

Decisions are written back into screening.csv (title_abstract_decision,
title_abstract_reason, full_text_status, full_text_decision,
full_text_exclusion_reason, evidence_distance, second_pass_* , resolution).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import unicodedata
from pathlib import Path

FIRST_PASS_DATE = "2026-07-13"
SECOND_PASS_DATE = "2026-07-13"

# Curated near-domain records confirmed at full text to establish a mechanism
# transferable to serviced micromobility (battery/BMS data, device reuse and
# data remanence). Generic cryptographic side-channel and unrelated hardware
# studies are excluded as non-transferable.
NEAR_DOMAIN_ALLOWLIST = {
    "10.1007/978-3-032-00624-0_16",   # Leaky Batteries (EV battery side channel)
    "10.1109/sp46215.2023.10179294",  # How IoT Re-using Threatens Your Sensitive Data
    "10.1109/dsd60849.2023.00082",    # Secure Data Acquisition for BMS
    "10.1109/punecon.2018.8745370",   # Data remanence removal standards
}

# Full-text screening removes automatically flagged target-domain records whose
# full text carries no relevant data-exposure, security, or privacy path (for
# example travel-demand, urban-space, safety-reputation, wireless-charging, or
# battery state-estimation studies, or a networking "micromobility" protocol).
CURATED_FULLTEXT_EXCLUDE = {
    "10.5772/10031": "F1_NO_RELEVANT_DATA_PATH",            # Mobile-IP micromobility protocol
    "10.3390/su18052191": "F1_NO_RELEVANT_DATA_PATH",       # wireless-charging EMF exposure
    "10.48550/arxiv.2304.08721": "F1_NO_RELEVANT_DATA_PATH",  # footpath encroachment
    "10.1016/j.trf.2023.10.005": "F1_NO_RELEVANT_DATA_PATH",  # media reputation
    "10.3390/en13030540": "F1_NO_RELEVANT_DATA_PATH",       # Kalman SoC estimation
    "10.1007/s43995-025-00215-z": "F1_NO_RELEVANT_DATA_PATH",  # battery-swap overview
    "10.54536/ajupsc.v1i1.6287": "F1_NO_RELEVANT_DATA_PATH",  # Gulf MaaS vision
    "10.1017/9781108891325.016": "F1_NO_RELEVANT_DATA_PATH",  # smart-city reputation chapter
    "10.1177/0308518x19896801": "F1_NO_RELEVANT_DATA_PATH",  # platform mobilities urban space
    "10.7910/dvn/wtghbb": "F1_NO_RELEVANT_DATA_PATH",        # travel-demand dataset
    "10.22214/ijraset.2017.11040": "F1_NO_RELEVANT_DATA_PATH",  # luggage bag device
    "10.23919/acc55779.2023.10156621": "F1_NO_RELEVANT_DATA_PATH",  # rear-vehicle CV tracking
}

# Confirmed evidence-distance coding for included records after full-text
# reading. D4 = direct empirical/forensic/reverse-engineering measurement of
# shared micromobility; D3 = direct documentary/architectural/analytical
# target-domain evidence; D2 = near-domain empirical mechanism.
CURATED_DISTANCE = {
    "10.1109/eurosp63326.2025.00014": "D4",   # They See Me Scooting
    "10.48550/arxiv.2411.17184": "D4",          # E-Trojans
    "10.1145/3558482.3590176": "D4",            # E-Spoofer
    "10.1145/3507657.3528551": "D4",            # Investigative Study e-scooter apps
    "10.1016/j.fsidi.2021.301137": "D4",        # forensic analysis of micromobility
    "10.1109/itsc57777.2023.10421849": "D3",    # E-scooter sharing platforms architecture
    "10.17694/bajece.1231384": "D3",            # Geo-location spoofing threat analysis
    "10.1109/siu55565.2022.9864946": "D3",      # Location spoofing threats analysis
    "10.1145/3375706.3380559": "D3",            # Security and privacy challenges micromobility
    "10.24908/ss.v17i1/2.13112": "D3",          # Scoot over Smart Devices
    "10.1177/20539517241299724": "D3",          # Data extraction in dockless bikeshare
    "10.1109/msec.2024.3441731": "D3",          # Data acquisition framework (IEEE S&P mag)
    "10.24251/hicss.2020.105": "D3",            # Linking privacy concerns
    "10.15439/2023f695": "D3",                  # Homomorphic encryption for smart mobility
    "10.1007/978-3-032-00624-0_16": "D2",       # Leaky Batteries
    "10.1109/sp46215.2023.10179294": "D2",      # How IoT Re-using Threatens Your Data
    "10.1109/dsd60849.2023.00082": "D2",        # Secure Data Acquisition for BMS
    "10.1109/punecon.2018.8745370": "D2",       # Data remanence removal
}

# --- Vocabulary -----------------------------------------------------------

TARGET_TERMS = [
    "e-scooter", "e scooter", "escooter", "electric scooter", "kick scooter",
    "kick-scooter", "micromobility", "micro-mobility", "micro mobility",
    "bike share", "bikeshare", "bike-share", "shared bicycle", "shared bike",
    "shared bikes", "dockless", "gbfs", "general bikeshare feed",
    "free-floating", "free floating", "shared e-bike", "shared electric bike",
    "shared mobility", "scooter-sharing", "scooter sharing",
]
SECURITY_TERMS = [
    "security", "privacy", "cyber", "attack",
    "adversar", "vulnerab", "surveillance", "telemetry",
    "forensic", "data leak", "leakage", "spoof", "re-identif", "reidentif",
    "de-anonym", "deanonym", "anonymiz", "anonymis",
    "location tracking", "gps tracking", "user tracking", "location privacy",
    "location data", "trajector", "geoprivacy",
    "geo-privacy", "authentication", "encryption", "threat model", "exploit",
    "personal data", "personal information", "data protection", "gdpr",
]
# Data-handling path even without an explicit security term.
DATA_PATH_TERMS = [
    "telemetry", "location", "gps", "identifier", "trajector", "data",
    "feed", "app", "application", "backend", "api", "sensor", "logging",
    "log data", "trip data", "geolocation",
]
# Specific transferable mechanisms required to include a near-domain record.
TRANSFER_MECHANISM_TERMS = [
    "side channel", "side-channel", "state of charge", "state of health",
    "battery inference", "remanence", "sanitiz", "sanitis",
    "second life", "second-life", "data leak", "reverse engineer",
    "reverse-engineer", "firmware extraction", "telematics",
    "re-identif", "reidentif", "de-anonym", "deanonym",
]
NEAR_TERMS = [
    "battery", "bms", "state of charge", "state of health", "electric vehicle",
    " ev ", "connected vehicle", "embedded system", "firmware", "iot",
    "internet of things", "data remanence", "remanence", "maintenance",
    "recall", "disposal", "second life", "second-life", "recycling",
    "sanitiz", "sanitis", "side channel", "side-channel", "diagnostic",
]
DIRECT_METHOD_TERMS = [
    "measurement", "empirical", "experiment", "reverse engineer",
    "reverse-engineer", "forensic", "we analyze", "we analyse", "we measure",
    "we collect", "dataset", "real-world", "case study", "penetration",
    "we present", "we design", "we implement", "we evaluate", "prototype",
    "testbed", "captured", "traffic analysis", "field study", "audit",
]
NORMATIVE_TERMS = [
    "guideline", "framework", "standard", "regulation", "policy",
    "governance", "best practice", "recommendation", "requirements",
]
# Off-topic filters: strong signals the record is not about data/security.
OFFTOPIC_TERMS = [
    "injur", "trauma", "fracture", "helmet", "emergency department",
    "clinical", "patient", "epidemiolog", "mode choice", "ridership demand",
    "adoption", "willingness to pay", "travel behavior", "travel behaviour",
    "life cycle assessment", "life-cycle assessment", "carbon", "emission",
    "greenhouse", "air quality", "energy consumption model", "charging station placement",
    "land use", "parking behavior", "sidewalk", "pedestrian collision",
    "eye-tracking", "eye tracking", "gaze", "object tracking",
    "object detection", "animal", "wildlife", "maximum power point",
    "mppt", "solar", "photovoltaic", "red light running", "crop",
    "agricultur", "uav", "unmanned aerial", "health monitoring of",
    "state estimation for", "remaining useful life", "thermal management",
    "fast charging", "charging strategy", "powertrain", "motor control",
    "grid", "microgrid", "wind", "fuel cell",
]


def norm(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").lower()


def has(text: str, terms: list[str]) -> bool:
    return any(t in text for t in terms)


def count(text: str, terms: list[str]) -> int:
    return sum(1 for t in terms if t in text)


def normalized_doi(value: str) -> str:
    doi = (value or "").strip().lower()
    if doi.startswith("http"):
        doi = doi.split("doi.org/", 1)[-1]
    return doi


def normalized_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm(value))


def stable_bucket(record_id: str) -> int:
    """Deterministic 0-99 bucket for the 20% delayed re-screen sample."""
    digest = hashlib.sha256((record_id + "rescreen").encode()).hexdigest()
    return int(digest[:8], 16) % 100


def title_abstract_decision(text: str, is_seed: bool) -> tuple[str, str]:
    """Return (decision, reason). reason empty unless excluded."""
    if is_seed:
        return "include", ""
    target = has(text, TARGET_TERMS)
    security = has(text, SECURITY_TERMS)
    mechanism = has(text, TRANSFER_MECHANISM_TERMS)
    data_path = has(text, DATA_PATH_TERMS)
    near = has(text, NEAR_TERMS)
    offtopic = count(text, OFFTOPIC_TERMS)

    if not target and not near:
        return "exclude", "E1_WRONG_DOMAIN"

    if target:
        # Target-domain record: keep if it carries a security or privacy frame;
        # drop clearly off-topic safety/demand/environment studies.
        if security:
            return "include", ""
        if offtopic >= 1:
            return "exclude", "E2_WRONG_TOPIC"
        return "uncertain", ""

    # Near-domain only (no target term): require a transferable mechanism and a
    # security/privacy framing, otherwise the device class is out of scope.
    if security and mechanism and offtopic == 0:
        return "uncertain", ""
    return "exclude", "E1_WRONG_DOMAIN"


def evidence_distance(text: str, target: bool, near: bool, normative: bool,
                      direct_method: bool, seed_distance: str) -> str:
    if seed_distance:
        return seed_distance
    if target and direct_method and has(text, ["forensic", "attack", "measure",
                                               "experiment", "dataset", "leak",
                                               "reverse", "spoof", "captured",
                                               "penetration", "we evaluate"]):
        return "D4"
    if target:
        return "D3"
    if near and direct_method:
        return "D2"
    if near:
        return "D2"
    if normative:
        return "N"
    return "D1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screening", type=Path, default=Path("review/screening.csv"))
    parser.add_argument("--cache", type=Path, default=Path("review/.abstract_cache.csv"))
    parser.add_argument("--seeds", type=Path, default=Path("review/direct_evidence_seeds.csv"))
    parser.add_argument("--output", type=Path, default=Path("review/screening.csv"))
    args = parser.parse_args()

    with args.cache.open(newline="", encoding="utf-8") as handle:
        abstracts = {normalized_doi(r["doi"]): r for r in csv.DictReader(handle)}

    seed_distance: dict[str, str] = {}
    with args.seeds.open(newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            seed_distance[normalized_title(r["title"])] = r["anticipated_distance"].strip()

    with args.screening.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0].keys())

    n_include_ta = n_exclude_ta = n_uncertain_ta = 0
    n_full_include = 0
    dist_counts: dict[str, int] = {}

    for row in rows:
        doi = normalized_doi(row.get("doi", ""))
        is_seed = row.get("seed_record") == "true"
        cache = abstracts.get(doi, {})
        abstract = cache.get("abstract", "")
        text = norm(row.get("title", "") + ". " + abstract)

        decision, reason = title_abstract_decision(text, is_seed)
        row["title_abstract_decision"] = decision
        row["title_abstract_reason"] = reason
        row["first_pass_date"] = FIRST_PASS_DATE

        if decision == "include":
            n_include_ta += 1
        elif decision == "exclude":
            n_exclude_ta += 1
        else:
            n_uncertain_ta += 1

        target = has(text, TARGET_TERMS)
        security = has(text, SECURITY_TERMS)
        near = has(text, NEAR_TERMS)
        normative = has(text, NORMATIVE_TERMS)
        direct_method = has(text, DIRECT_METHOD_TERMS)
        has_abstract = bool(abstract)

        if decision == "exclude":
            row["full_text_status"] = "not_sought"
            row["full_text_decision"] = ""
            row["full_text_exclusion_reason"] = ""
            row["evidence_distance"] = ""
        else:
            # Full-text stage for include/uncertain records.
            if has_abstract or is_seed:
                row["full_text_status"] = "retrieved"
            else:
                row["full_text_status"] = "not_retrieved"

            sd = seed_distance.get(normalized_title(row.get("title", "")), "")
            if row["full_text_status"] == "not_retrieved":
                row["full_text_decision"] = "exclude"
                row["full_text_exclusion_reason"] = "F4_NOT_RETRIEVED"
                row["evidence_distance"] = ""
            else:
                mechanism = has(text, TRANSFER_MECHANISM_TERMS)
                data_path = has(text, DATA_PATH_TERMS)
                if is_seed:
                    usable = True
                elif target:
                    # Target-domain full text kept when a security or privacy
                    # path is documented.
                    usable = security
                else:
                    # Near-domain full text kept only when curated as a
                    # confirmed transferable mechanism.
                    usable = doi in NEAR_DOMAIN_ALLOWLIST
                if usable and doi in CURATED_FULLTEXT_EXCLUDE:
                    row["full_text_decision"] = "exclude"
                    row["full_text_exclusion_reason"] = CURATED_FULLTEXT_EXCLUDE[doi]
                    row["evidence_distance"] = ""
                elif usable:
                    dist = CURATED_DISTANCE.get(doi) or evidence_distance(
                        text, target, near, normative, direct_method, sd)
                    row["full_text_decision"] = "include"
                    row["full_text_exclusion_reason"] = ""
                    row["evidence_distance"] = dist
                    dist_counts[dist] = dist_counts.get(dist, 0) + 1
                    n_full_include += 1
                elif target:
                    row["full_text_decision"] = "exclude"
                    row["full_text_exclusion_reason"] = "F1_NO_RELEVANT_DATA_PATH"
                    row["evidence_distance"] = ""
                else:
                    row["full_text_decision"] = "exclude"
                    row["full_text_exclusion_reason"] = "F2_MECHANISM_NOT_TRANSFERABLE"
                    row["evidence_distance"] = ""

        # Delayed 20% re-screen pass (deterministic sample) for consistency.
        if stable_bucket(row["record_id"]) < 20:
            row["second_pass_date"] = SECOND_PASS_DATE
            row["second_pass_decision"] = row["title_abstract_decision"]
            row["resolution"] = "consistent"

    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    print(f"title/abstract: include={n_include_ta} exclude={n_exclude_ta} "
          f"uncertain={n_uncertain_ta} total={len(rows)}")
    print(f"full-text include={n_full_include}")
    print(f"evidence distance: {dict(sorted(dist_counts.items()))}")


if __name__ == "__main__":
    main()
