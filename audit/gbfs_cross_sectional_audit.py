#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


GBFS_COMMIT = "4b7227fb1f136d83bcea2658b135fc52a83a92d9"
REGISTRY_URL = (
    "https://raw.githubusercontent.com/MobilityData/gbfs/"
    f"{GBFS_COMMIT}/systems.csv"
)
USER_AGENT = "DischargedSecretsGBFSAudit/0.1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a privacy-preserving cross-sectional audit of registered GBFS feeds."
    )
    parser.add_argument("--registry-output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--metadata-output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--limit", type=int)
    return parser.parse_args()


def fetch_bytes(url: str, timeout: int = 15) -> tuple[bytes, int]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = ""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read(), response.status
        except (urllib.error.URLError, TimeoutError) as error:
            last_error = f"{type(error).__name__}: {error}"
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError(last_error)


def fetch_json(url: str) -> tuple[dict, int, str]:
    payload, status = fetch_bytes(url)
    digest = hashlib.sha256(payload).hexdigest()
    decoded = json.loads(payload.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("Expected a JSON object")
    return decoded, status, digest


def domain(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")


def safe_identifier(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    return normalized or hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def discovery_feeds(payload: dict) -> tuple[list[dict], str]:
    version = payload.get("version")
    declared_version = version if isinstance(version, str) else ""
    data = payload.get("data", {})
    if not isinstance(data, dict):
        return [], declared_version
    blocks: list[dict] = []
    if isinstance(data.get("feeds"), list):
        blocks.append(data)
    else:
        for value in data.values():
            if isinstance(value, dict) and isinstance(value.get("feeds"), list):
                blocks.append(value)
    feeds: list[dict] = []
    for block in blocks:
        values = block.get("feeds", [])
        if isinstance(values, list):
            feeds.extend(item for item in values if isinstance(item, dict))
    return feeds, declared_version


def find_feed(feeds: list[dict], names: tuple[str, ...]) -> dict | None:
    for feed in feeds:
        name = feed.get("name")
        url = feed.get("url")
        if name in names and isinstance(url, str) and url:
            return feed
    return None


def record_array(payload: dict, keys: tuple[str, ...]) -> list[dict]:
    data = payload.get("data", {})
    if not isinstance(data, dict):
        return []
    for key in keys:
        values = data.get(key)
        if isinstance(values, list):
            return [value for value in values if isinstance(value, dict)]
    return []


def string_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def audit_row(row_number: int, registry_row: dict[str, str]) -> dict[str, str]:
    result = {
        "registry_row": str(row_number),
        "country_code": registry_row.get("Country Code", ""),
        "name": registry_row.get("Name", ""),
        "location": registry_row.get("Location", ""),
        "system_id": registry_row.get("System ID", ""),
        "website_domain": domain(registry_row.get("URL", "")),
        "auto_discovery_domain": domain(registry_row.get("Auto-Discovery URL", "")),
        "supported_versions": registry_row.get("Supported Versions", ""),
        "authentication_type": registry_row.get("Authentication Type", ""),
        "auto_discovery_status": "",
        "auto_discovery_sha256": "",
        "declared_version": "",
        "feed_names": "",
        "has_vehicle_status": "false",
        "vehicle_status_status": "",
        "vehicle_status_sha256": "",
        "vehicle_count": "",
        "vehicle_field_names": "",
        "has_vehicle_id": "false",
        "has_location_fields": "false",
        "has_last_reported": "false",
        "has_battery_percent": "false",
        "has_range": "false",
        "has_deep_link": "false",
        "vehicle_types_status": "",
        "vehicle_types_sha256": "",
        "vehicle_type_count": "",
        "form_factors": "",
        "propulsion_types": "",
        "motorized_declared": "false",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "error_stage": "",
        "error_message": "",
    }
    discovery_url = registry_row.get("Auto-Discovery URL", "")
    if not discovery_url:
        result["error_stage"] = "registry"
        result["error_message"] = "missing auto-discovery URL"
        return result
    try:
        discovery, status, digest = fetch_json(discovery_url)
        result["auto_discovery_status"] = str(status)
        result["auto_discovery_sha256"] = digest
        feeds, declared_version = discovery_feeds(discovery)
        result["declared_version"] = declared_version
        feed_names = sorted(
            {
                name
                for feed in feeds
                if isinstance((name := feed.get("name")), str)
            }
        )
        result["feed_names"] = ";".join(feed_names)
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        result["error_stage"] = "auto_discovery"
        result["error_message"] = f"{type(error).__name__}: {error}".strip()[:500]
        return result

    types_feed = find_feed(feeds, ("vehicle_types",))
    if types_feed:
        try:
            types_payload, status, digest = fetch_json(str(types_feed["url"]))
            result["vehicle_types_status"] = str(status)
            result["vehicle_types_sha256"] = digest
            type_records = record_array(types_payload, ("vehicle_types",))
            result["vehicle_type_count"] = str(len(type_records))
            form_factors: set[str] = set()
            propulsion_types: set[str] = set()
            for record in type_records:
                form_factors.update(string_values(record.get("form_factor")))
                propulsion_types.update(string_values(record.get("propulsion_type")))
            result["form_factors"] = ";".join(sorted(form_factors))
            result["propulsion_types"] = ";".join(sorted(propulsion_types))
            motorized = any(
                value.lower() not in {"human", "human-powered"}
                for value in propulsion_types
            )
            result["motorized_declared"] = str(motorized).lower()
        except (RuntimeError, ValueError, json.JSONDecodeError) as error:
            result["error_stage"] = "vehicle_types"
            result["error_message"] = f"{type(error).__name__}: {error}".strip()[:500]

    status_feed = find_feed(feeds, ("vehicle_status", "free_bike_status"))
    if not status_feed:
        return result
    result["has_vehicle_status"] = "true"
    try:
        status_payload, status, digest = fetch_json(str(status_feed["url"]))
        result["vehicle_status_status"] = str(status)
        result["vehicle_status_sha256"] = digest
        vehicles = record_array(status_payload, ("vehicles", "bikes"))
        result["vehicle_count"] = str(len(vehicles))
        fields: set[str] = set()
        for vehicle in vehicles:
            fields.update(vehicle.keys())
        result["vehicle_field_names"] = ";".join(sorted(fields))
        result["has_vehicle_id"] = str(
            bool({"vehicle_id", "bike_id"} & fields)
        ).lower()
        result["has_location_fields"] = str(
            {"lat", "lon"}.issubset(fields)
        ).lower()
        result["has_last_reported"] = str("last_reported" in fields).lower()
        result["has_battery_percent"] = str(
            "current_fuel_percent" in fields
        ).lower()
        result["has_range"] = str("current_range_meters" in fields).lower()
        result["has_deep_link"] = str("rental_uris" in fields).lower()
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        if not result["error_stage"]:
            result["error_stage"] = "vehicle_status"
            result["error_message"] = f"{type(error).__name__}: {error}".strip()[:500]
    return result


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    registry_payload, registry_status = fetch_bytes(REGISTRY_URL)
    registry_digest = hashlib.sha256(registry_payload).hexdigest()
    args.registry_output.parent.mkdir(parents=True, exist_ok=True)
    args.registry_output.write_bytes(registry_payload)
    decoded_registry = registry_payload.decode("utf-8-sig").splitlines()
    registry_rows = list(csv.DictReader(decoded_registry))
    if args.limit is not None:
        registry_rows = registry_rows[: args.limit]

    results: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(audit_row, index, row): index
            for index, row in enumerate(registry_rows, start=1)
        }
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: int(item["registry_row"]))

    fields = list(results[0].keys()) if results else []
    write_csv(args.audit_output, results, fields)
    metadata = [
        {
            "registry_url": REGISTRY_URL,
            "registry_commit": GBFS_COMMIT,
            "registry_http_status": str(registry_status),
            "registry_sha256": registry_digest,
            "registry_rows_total": str(len(decoded_registry) - 1),
            "registry_rows_audited": str(len(results)),
            "audit_started_from_utc": min(
                (row["fetched_at_utc"] for row in results),
                default="",
            ),
            "audit_completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "workers": str(args.workers),
            "user_agent": USER_AGENT,
        }
    ]
    write_csv(args.metadata_output, metadata, list(metadata[0].keys()))
    reachable = sum(row["auto_discovery_status"] == "200" for row in results)
    vehicle_feeds = sum(row["has_vehicle_status"] == "true" for row in results)
    print(f"Audited {len(results)} registry entries")
    print(f"Reachable auto-discovery endpoints: {reachable}")
    print(f"Entries declaring vehicle-status feeds: {vehicle_feeds}")


if __name__ == "__main__":
    main()
