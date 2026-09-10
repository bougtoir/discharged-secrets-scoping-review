#!/usr/bin/env python3
"""Build the study-level extraction table for included records.

Extraction content was coded from the full text / author abstract of each
included study by the single reviewer. Bibliographic fields (authors, venue,
year) are joined from the frozen candidate corpus so citations stay consistent
with the screening record.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def nd(value: str) -> str:
    d = (value or "").strip().lower()
    return d.split("doi.org/", 1)[-1] if d.startswith("http") else d


# Per-study extraction, keyed by normalized DOI. Ratings use the protocol's
# four-level scale: strong / moderate / weak / not_reported.
EXTRACTION: dict[str, dict[str, str]] = {
    "10.1109/eurosp63326.2025.00014": {
        "study_country": "Germany", "device_or_service": "Shared e-scooter and e-bike systems (public provider feeds)",
        "study_design": "Longitudinal measurement of public sharing feeds",
        "sample_or_corpus": "Multiple operators, long-term city-scale observation",
        "data_fields": "Vehicle location, state changes, identifiers",
        "access_path": "Public provider application programming interface / feed",
        "observation_or_attack": "Link vehicle state changes to individual trips and mobility patterns",
        "measured_outcome": "Re-identification and trip linkage from public feeds",
        "key_result": "Public feed state changes reconstruct individual mobility patterns exploitable for stalking or burglary",
        "limitations": "Provider- and city-specific; no ground-truth rider identity",
        "reproducibility_artifact": "Method described; feeds public",
        "lifecycle_stage": "Operation",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "strong", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Direct public-feed privacy-leakage measurement; anchors WP2 rationale",
    },
    "10.48550/arxiv.2411.17184": {
        "study_country": "Italy", "device_or_service": "Xiaomi M365 and ES3 e-scooters with companion app",
        "study_design": "Reverse engineering and security/privacy assessment",
        "sample_or_corpus": "Two e-scooter models and companion app",
        "data_fields": "BMS data, motor-controller data, radio interface, app telemetry",
        "access_path": "Local wireless (BLE), internal buses, companion app",
        "observation_or_attack": "Four design vulnerabilities including remote code execution and data leaks",
        "measured_outcome": "Confidentiality, integrity, availability, and privacy impact",
        "key_result": "Battery-powered embedded internals expose tracking, DoS, ransomware, and data-leak surfaces",
        "limitations": "Vendor-specific; two models; lab conditions",
        "reproducibility_artifact": "Detailed methodology; responsible disclosure",
        "lifecycle_stage": "Operation; Maintenance",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Direct BMS/embedded evidence for on-device data generation",
    },
    "10.1145/3558482.3590176": {
        "study_country": "Italy", "device_or_service": "Xiaomi e-scooter ecosystem and Mi Home app",
        "study_design": "Protocol reverse engineering and attack/defense experiments",
        "sample_or_corpus": "Market-leading e-scooter models",
        "data_fields": "BLE control channel, authentication tokens",
        "access_path": "Bluetooth Low Energy proprietary protocol",
        "observation_or_attack": "Break proprietary BLE security; theft and lockout attacks",
        "measured_outcome": "Security, privacy, and safety impact of protocol weaknesses",
        "key_result": "Proprietary BLE protocol exploitable to steal or disable scooters and expose data",
        "limitations": "Single vendor; requires BLE proximity",
        "reproducibility_artifact": "Defense prototype released",
        "lifecycle_stage": "Operation",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Direct device ecosystem security experiment",
    },
    "10.1145/3507657.3528551": {
        "study_country": "United States", "device_or_service": "Mobile e-scooter rental applications",
        "study_design": "Static/dynamic app privacy measurement",
        "sample_or_corpus": "Multiple e-scooter rental apps (Android)",
        "data_fields": "Location, device identifiers, personal and account data, third-party SDKs",
        "access_path": "Mobile application and embedded trackers",
        "observation_or_attack": "Quantify collected data, permissions, and third-party data flows",
        "measured_outcome": "Extent of privacy-sensitive collection and sharing",
        "key_result": "Rental apps collect privacy-sensitive data as a functional requirement and embed third-party trackers",
        "limitations": "Android focus; app versions time-bound",
        "reproducibility_artifact": "Methodology documented",
        "lifecycle_stage": "Operation",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "strong", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Direct app-layer privacy measurement",
    },
    "10.1016/j.fsidi.2021.301137": {
        "study_country": "Germany", "device_or_service": "Micromobility rental apps (bikes and e-scooters)",
        "study_design": "Mobile digital forensic analysis",
        "sample_or_corpus": "Several micromobility apps on mobile devices",
        "data_fields": "Trip history, location artifacts, account and payment traces",
        "access_path": "Forensic acquisition of a device / app storage",
        "observation_or_attack": "Recover movement-related artifacts persisting on devices",
        "measured_outcome": "Forensic recoverability of movement and account data",
        "key_result": "Micromobility apps retain recoverable movement and account artifacts of investigative value",
        "limitations": "App/OS-version dependent; controlled devices",
        "reproducibility_artifact": "Forensic procedure documented",
        "lifecycle_stage": "Operation; Return",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Direct forensic evidence of data persistence",
    },
    "10.1109/itsc57777.2023.10421849": {
        "study_country": "United Kingdom", "device_or_service": "E-scooter sharing platforms (ESPs)",
        "study_design": "Architecture and threat analysis",
        "sample_or_corpus": "Reference ESP architecture",
        "data_fields": "Platform, backend, app, and vehicle data flows",
        "access_path": "System architecture components and interfaces",
        "observation_or_attack": "Enumerate architecture, threats, and cybersecurity risks",
        "measured_outcome": "Threat and risk mapping to platform components",
        "key_result": "ESP architecture exposes resource abuse, DoS, and personal-data breach surfaces",
        "limitations": "Analytical; no device experiments",
        "reproducibility_artifact": "Architecture documented",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "moderate",
        "extractor_note": "Documentary platform architecture and threat mapping",
    },
    "10.17694/bajece.1231384": {
        "study_country": "Turkey", "device_or_service": "E-scooter sharing (geo-location services)",
        "study_design": "Threat analysis and prevention framework",
        "sample_or_corpus": "E-scooter geo-location service model",
        "data_fields": "GPS / positioning data",
        "access_path": "Positioning service and application",
        "observation_or_attack": "Analyze location-spoofing threats; propose prevention",
        "measured_outcome": "Spoofing threat characterization and mitigation design",
        "key_result": "E-scooter positioning is vulnerable to spoofing affecting cost, reliability, and safety",
        "limitations": "Analytical; limited empirical validation",
        "reproducibility_artifact": "Framework described",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "weak", "reproducibility_rating": "weak",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Documentary location-security analysis",
    },
    "10.1109/siu55565.2022.9864946": {
        "study_country": "Turkey", "device_or_service": "E-scooter sharing (GPS/Wi-Fi positioning)",
        "study_design": "Threat analysis",
        "sample_or_corpus": "E-scooter positioning model",
        "data_fields": "GPS and Wi-Fi positioning data",
        "access_path": "Positioning service",
        "observation_or_attack": "Characterize positioning spoofing threats",
        "measured_outcome": "Spoofing threat surface for shared e-scooters",
        "key_result": "Shared e-scooter positioning inherits known spoofing vulnerabilities",
        "limitations": "Analytical; conference short paper",
        "reproducibility_artifact": "Method described",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "weak", "reproducibility_rating": "weak",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Documentary positioning-threat analysis",
    },
    "10.1145/3375706.3380559": {
        "study_country": "United States", "device_or_service": "Intelligent urban micromobility ecosystem",
        "study_design": "Security/privacy challenge analysis",
        "sample_or_corpus": "Micromobility vehicles, providers, users",
        "data_fields": "Vehicle, provider, and rider data",
        "access_path": "Ecosystem attack surfaces",
        "observation_or_attack": "Map security and privacy challenges across the ecosystem",
        "measured_outcome": "Challenge taxonomy",
        "key_result": "The vehicle-provider-rider ecosystem is an exploitable attack surface for security and privacy",
        "limitations": "Analytical; forward-looking",
        "reproducibility_artifact": "Taxonomy documented",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "moderate",
        "extractor_note": "Foundational documentary threat framing",
    },
    "10.24908/ss.v17i1/2.13112": {
        "study_country": "United States", "device_or_service": "Rental scooters (Bird, Lime, Spin)",
        "study_design": "Surveillance and data-practice analysis",
        "sample_or_corpus": "Major North American operators",
        "data_fields": "Location, phone number, phone metadata, account data",
        "access_path": "Mobile app and scooter-mounted GPS",
        "observation_or_attack": "Characterize identifying data collection and downstream sharing",
        "measured_outcome": "Identifiability and data-sharing exposure",
        "key_result": "Rental scooters yield a uniquely identifying rider dataset that may be shared or sold",
        "limitations": "Descriptive; policy-era specific",
        "reproducibility_artifact": "Documentary sources",
        "lifecycle_stage": "Operation; Data sharing",
        "data_provenance": "moderate", "device_sample_coverage": "moderate", "reproducibility_rating": "weak",
        "access_path_realism": "strong", "outcome_validity": "moderate", "external_validity": "moderate",
        "extractor_note": "Documentary surveillance/data-brokerage evidence",
    },
    "10.1109/msec.2024.3441731": {
        "study_country": "Japan", "device_or_service": "Micromobility vehicles (data-acquisition testbed)",
        "study_design": "Measurement framework with experiments",
        "sample_or_corpus": "Diverse micromobility systems",
        "data_fields": "Cyberphysical signals for driving-risk features",
        "access_path": "Instrumented data acquisition in real space",
        "observation_or_attack": "Quantify cyberphysical-attack impact on micromobility",
        "measured_outcome": "Security-risk measurement across systems",
        "key_result": "A reproducible framework measures cyberphysical security-attack impact on micromobility vehicles",
        "limitations": "Framework stage; augmentation ongoing",
        "reproducibility_artifact": "Framework described",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "moderate",
        "extractor_note": "Documentary/experimental data-acquisition framework",
    },
    "10.24251/hicss.2020.105": {
        "study_country": "South Korea", "device_or_service": "E-scooter sharing platforms",
        "study_design": "Survey / behavioral privacy study",
        "sample_or_corpus": "E-scooter platform users",
        "data_fields": "Traceable route/trip information",
        "access_path": "Platform data collection and disclosure practices",
        "observation_or_attack": "Model privacy concern for traceable information (PCTI)",
        "measured_outcome": "User privacy concern and protective responses",
        "key_result": "Traceable route information drives distinct privacy concern and protective responses",
        "limitations": "Self-report; single-country sample",
        "reproducibility_artifact": "Instrument described",
        "lifecycle_stage": "Operation",
        "data_provenance": "moderate", "device_sample_coverage": "not_reported", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Documentary user-privacy-concern evidence",
    },
    "10.1177/20539517241299724": {
        "study_country": "United Kingdom", "device_or_service": "Dockless bikeshare platforms",
        "study_design": "Qualitative user-perspective study",
        "sample_or_corpus": "Dockless bikeshare users",
        "data_fields": "Personal data and travel trajectories",
        "access_path": "Platform data extraction and monetization",
        "observation_or_attack": "Examine data extraction and user perception",
        "measured_outcome": "User awareness of trajectory data extraction",
        "key_result": "Trajectory data extraction is core to bikeshare business models but poorly understood by users",
        "limitations": "Qualitative; context-specific",
        "reproducibility_artifact": "Methods documented",
        "lifecycle_stage": "Operation; Data sharing",
        "data_provenance": "moderate", "device_sample_coverage": "not_reported", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Documentary trajectory-extraction evidence",
    },
    "10.15439/2023f695": {
        "study_country": "Germany", "device_or_service": "Smart-mobility platforms (incl. rental bikes, e-scooters)",
        "study_design": "Feasibility study of privacy-enhancing technology",
        "sample_or_corpus": "Mobility-platform data-sharing scenario",
        "data_fields": "Reservation, routing, billing personal data",
        "access_path": "Multi-party mobility platform",
        "observation_or_attack": "Assess fully homomorphic encryption feasibility",
        "measured_outcome": "Practicality of FHE for privacy protection",
        "key_result": "Smart mobility shares sensitive personal data across parties; FHE mitigations remain costly",
        "limitations": "Feasibility analysis; limited deployment realism",
        "reproducibility_artifact": "Analysis described",
        "lifecycle_stage": "Operation; Data sharing",
        "data_provenance": "moderate", "device_sample_coverage": "not_reported", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Documentary privacy-engineering feasibility evidence",
    },
    "10.1007/978-3-032-00624-0_16": {
        "study_country": "Italy", "device_or_service": "Electric vehicles (battery side channel)",
        "study_design": "Side-channel measurement experiments",
        "sample_or_corpus": "EV battery/telemetry signals",
        "data_fields": "Battery current/voltage and related telemetry",
        "access_path": "Battery / vehicle bus side channel",
        "observation_or_attack": "Infer operational information from battery side channels",
        "measured_outcome": "Inference accuracy from non-positional battery signals",
        "key_result": "Battery side channels leak operational information without explicit location data",
        "limitations": "EV domain; transfer to shared scooters unverified",
        "reproducibility_artifact": "Experimental methodology",
        "lifecycle_stage": "Operation",
        "data_provenance": "strong", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "strong", "external_validity": "weak",
        "extractor_note": "Near-domain battery-inference mechanism (transfer not demonstrated)",
    },
    "10.1109/sp46215.2023.10179294": {
        "study_country": "China / United States", "device_or_service": "Used IoT devices (resale market)",
        "study_design": "Systematic empirical study of data disposal",
        "sample_or_corpus": "Used IoT devices from resale channels",
        "data_fields": "Credentials, biometrics, residual user data",
        "access_path": "Second-hand device acquisition and inspection",
        "observation_or_attack": "Assess whether users properly dispose of residual data",
        "measured_outcome": "Prevalence of residual sensitive data after resale",
        "key_result": "Resold IoT devices frequently retain recoverable sensitive user data",
        "limitations": "General IoT; not micromobility-specific",
        "reproducibility_artifact": "Methodology documented",
        "lifecycle_stage": "Return; Second-life; Disposal",
        "data_provenance": "strong", "device_sample_coverage": "strong", "reproducibility_rating": "moderate",
        "access_path_realism": "strong", "outcome_validity": "strong", "external_validity": "moderate",
        "extractor_note": "Near-domain device-reuse remanence mechanism",
    },
    "10.1109/dsd60849.2023.00082": {
        "study_country": "Austria", "device_or_service": "Battery management systems (EV batteries)",
        "study_design": "Secure data-acquisition architecture",
        "sample_or_corpus": "BMS-to-cloud data pipeline",
        "data_fields": "Battery lifecycle data, battery-passport records",
        "access_path": "BMS with cloud integration",
        "observation_or_attack": "Secure BMS data across manufacturing, second-life, recycling",
        "measured_outcome": "Security design for lifecycle battery data",
        "key_result": "Regulated battery passports generate lifecycle data spanning use, second-life, and recycling",
        "limitations": "Design study; battery-domain scope",
        "reproducibility_artifact": "Architecture described",
        "lifecycle_stage": "Manufacturing; Second-life; Recycling",
        "data_provenance": "moderate", "device_sample_coverage": "moderate", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Near-domain battery-lifecycle data mechanism and regulation link",
    },
    "10.1109/punecon.2018.8745370": {
        "study_country": "India", "device_or_service": "Cloud storage media",
        "study_design": "Standards and techniques review",
        "sample_or_corpus": "Cloud storage sanitization methods",
        "data_fields": "Residual data (identifiers, secrets, records)",
        "access_path": "Storage media remanence",
        "observation_or_attack": "Review data-remanence removal standards and techniques",
        "measured_outcome": "Applicability of sanitization techniques",
        "key_result": "Inadequate media sanitization leaves recoverable residual data via remanence",
        "limitations": "Cloud-storage domain; review paper",
        "reproducibility_artifact": "Documented techniques",
        "lifecycle_stage": "Disposal; Recycling",
        "data_provenance": "moderate", "device_sample_coverage": "not_reported", "reproducibility_rating": "moderate",
        "access_path_realism": "moderate", "outcome_validity": "moderate", "external_validity": "weak",
        "extractor_note": "Near-domain remanence/sanitization mechanism",
    },
}


def main() -> None:
    screening = {}
    with (ROOT / "screening.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["full_text_decision"] == "include":
                screening[nd(row["doi"])] = row
    candidates = {}
    with (ROOT / "candidates.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            candidates[nd(row["doi"])] = row

    fieldnames = [
        "record_id", "citation", "study_country", "device_or_service",
        "study_design", "sample_or_corpus", "data_fields", "access_path",
        "observation_or_attack", "measured_outcome", "key_result",
        "limitations", "reproducibility_artifact", "lifecycle_stage",
        "evidence_distance", "data_provenance", "device_sample_coverage",
        "reproducibility_rating", "access_path_realism", "outcome_validity",
        "external_validity", "extractor_note",
    ]

    missing = set(screening) - set(EXTRACTION)
    if missing:
        raise SystemExit(f"missing extraction for: {sorted(missing)}")

    out_rows = []
    for doi, srow in screening.items():
        ext = EXTRACTION[doi]
        cand = candidates.get(doi, {})
        authors = cand.get("authors", "").split(";")
        first_author = authors[0].strip() if authors and authors[0] else "n.a."
        last = first_author.split()[-1] if first_author != "n.a." else "n.a."
        etal = " et al." if len(authors) > 1 else ""
        citation = f"{last}{etal} ({srow.get('year','')}). {srow.get('title','')}. {cand.get('venue','')}. doi:{doi}"
        row = {"record_id": srow["record_id"], "citation": citation,
               "evidence_distance": srow["evidence_distance"]}
        row.update(ext)
        out_rows.append({k: row.get(k, "") for k in fieldnames})

    order = {"D4": 0, "D3": 1, "D2": 2, "D1": 3, "N": 4}
    out_rows.sort(key=lambda r: (order.get(r["evidence_distance"], 9), r["citation"]))

    out_path = ROOT / "evidence_extraction.csv"
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {len(out_rows)} extraction rows to {out_path.name}")


if __name__ == "__main__":
    main()
