#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


USER_AGENT = "DischargedSecretsScopingReview/0.1"
START_DATE = "2010-01-01"
OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search open bibliographic APIs and build a deduplicated candidate corpus."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--per-source", type=int, default=100)
    return parser.parse_args()


def fetch_json(url: str) -> tuple[dict, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = ""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read()
            digest = hashlib.sha256(payload).hexdigest()
            decoded = json.loads(payload.decode("utf-8"))
            if not isinstance(decoded, dict):
                raise ValueError("Expected a JSON object")
            return decoded, digest
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
            last_error = str(error)
            if attempt < 2:
                time.sleep(2**attempt)
    raise RuntimeError(f"Request failed after three attempts: {url}; {last_error}")


def normalize_doi(value: object) -> str:
    if not isinstance(value, str):
        return ""
    doi = value.strip().lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    return doi


def normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).lower()
    return re.sub(r"[^a-z0-9]+", "", normalized)


def openalex_authors(work: dict) -> str:
    names: list[str] = []
    authorships = work.get("authorships", [])
    if not isinstance(authorships, list):
        return ""
    for authorship in authorships:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author", {})
        if isinstance(author, dict):
            name = author.get("display_name")
            if isinstance(name, str) and name:
                names.append(name)
    return "; ".join(names)


def openalex_venue(work: dict) -> str:
    primary_location = work.get("primary_location", {})
    if not isinstance(primary_location, dict):
        return ""
    source = primary_location.get("source", {})
    if not isinstance(source, dict):
        return ""
    name = source.get("display_name")
    return name if isinstance(name, str) else ""


def crossref_year(item: dict) -> str:
    for field in ("published-print", "published-online", "published", "issued", "created"):
        date = item.get(field, {})
        if not isinstance(date, dict):
            continue
        parts = date.get("date-parts", [])
        if (
            isinstance(parts, list)
            and parts
            and isinstance(parts[0], list)
            and parts[0]
            and isinstance(parts[0][0], int)
        ):
            return str(parts[0][0])
    return ""


def crossref_authors(item: dict) -> str:
    names: list[str] = []
    authors = item.get("author", [])
    if not isinstance(authors, list):
        return ""
    for author in authors:
        if not isinstance(author, dict):
            continue
        given = author.get("given")
        family = author.get("family")
        parts = [
            part
            for part in (given, family)
            if isinstance(part, str) and part.strip()
        ]
        if parts:
            names.append(" ".join(parts))
    return "; ".join(names)


def add_candidate(
    candidates: dict[str, dict[str, str]],
    candidate: dict[str, str],
    query_id: str,
    source: str,
) -> None:
    doi = normalize_doi(candidate.get("doi", ""))
    title_key = normalize_title(candidate.get("title", ""))
    key = f"doi:{doi}" if doi else f"title:{title_key}"
    if not title_key:
        return
    if key not in candidates:
        candidate["doi"] = doi
        candidate["query_ids"] = query_id
        candidate["source_apis"] = source
        candidates[key] = candidate
        return
    existing = candidates[key]
    existing_queries = set(filter(None, existing["query_ids"].split(";")))
    existing_sources = set(filter(None, existing["source_apis"].split(";")))
    existing_queries.add(query_id)
    existing_sources.add(source)
    existing["query_ids"] = ";".join(sorted(existing_queries))
    existing["source_apis"] = ";".join(sorted(existing_sources))
    for field in ("year", "url", "venue", "authors", "work_type"):
        if not existing.get(field) and candidate.get(field):
            existing[field] = candidate[field]


def search_openalex(
    query_id: str,
    query: str,
    per_source: int,
    candidates: dict[str, dict[str, str]],
) -> dict[str, str]:
    params = urllib.parse.urlencode(
        {
            "search": query,
            "filter": f"from_publication_date:{START_DATE}",
            "per-page": min(per_source, 200),
        }
    )
    url = f"{OPENALEX_URL}?{params}"
    payload, digest = fetch_json(url)
    results = payload.get("results", [])
    if not isinstance(results, list):
        results = []
    for work in results:
        if not isinstance(work, dict):
            continue
        title = work.get("display_name")
        if not isinstance(title, str):
            continue
        year = work.get("publication_year")
        work_type = work.get("type")
        primary_location = work.get("primary_location", {})
        landing_page = ""
        if isinstance(primary_location, dict):
            candidate_url = primary_location.get("landing_page_url")
            if isinstance(candidate_url, str):
                landing_page = candidate_url
        add_candidate(
            candidates,
            {
                "title": title,
                "year": str(year) if isinstance(year, int) else "",
                "doi": normalize_doi(work.get("doi")),
                "url": landing_page,
                "venue": openalex_venue(work),
                "authors": openalex_authors(work),
                "work_type": work_type if isinstance(work_type, str) else "",
            },
            query_id,
            "OpenAlex",
        )
    meta = payload.get("meta", {})
    total = meta.get("count", "") if isinstance(meta, dict) else ""
    return {
        "query_id": query_id,
        "source_api": "OpenAlex",
        "query": query,
        "request_url": url,
        "total_results": str(total),
        "returned_results": str(len(results)),
        "response_sha256": digest,
        "searched_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def search_crossref(
    query_id: str,
    query: str,
    per_source: int,
    candidates: dict[str, dict[str, str]],
) -> dict[str, str]:
    params = urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "filter": f"from-pub-date:{START_DATE}",
            "rows": min(per_source, 1000),
            "select": "DOI,title,author,published,published-print,published-online,issued,created,URL,container-title,type",
        }
    )
    url = f"{CROSSREF_URL}?{params}"
    payload, digest = fetch_json(url)
    message = payload.get("message", {})
    if not isinstance(message, dict):
        message = {}
    items = message.get("items", [])
    if not isinstance(items, list):
        items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title_values = item.get("title", [])
        title = (
            title_values[0]
            if isinstance(title_values, list)
            and title_values
            and isinstance(title_values[0], str)
            else ""
        )
        container_values = item.get("container-title", [])
        venue = (
            container_values[0]
            if isinstance(container_values, list)
            and container_values
            and isinstance(container_values[0], str)
            else ""
        )
        url_value = item.get("URL")
        work_type = item.get("type")
        add_candidate(
            candidates,
            {
                "title": title,
                "year": crossref_year(item),
                "doi": normalize_doi(item.get("DOI")),
                "url": url_value if isinstance(url_value, str) else "",
                "venue": venue,
                "authors": crossref_authors(item),
                "work_type": work_type if isinstance(work_type, str) else "",
            },
            query_id,
            "Crossref",
        )
    return {
        "query_id": query_id,
        "source_api": "Crossref",
        "query": query,
        "request_url": url,
        "total_results": str(message.get("total-results", "")),
        "returned_results": str(len(items)),
        "response_sha256": digest,
        "searched_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def load_queries(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Query config must be a JSON array")
    queries: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Each query entry must be a JSON object")
        query_id = item.get("id")
        query = item.get("query")
        if not isinstance(query_id, str) or not isinstance(query, str):
            raise ValueError("Each query entry requires string id and query fields")
        queries.append({"id": query_id, "query": query})
    return queries


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    queries = load_queries(args.config)
    candidates: dict[str, dict[str, str]] = {}
    logs: list[dict[str, str]] = []
    for entry in queries:
        logs.append(
            search_openalex(
                entry["id"],
                entry["query"],
                args.per_source,
                candidates,
            )
        )
        logs.append(
            search_crossref(
                entry["id"],
                entry["query"],
                args.per_source,
                candidates,
            )
        )
    candidate_rows = sorted(
        candidates.values(),
        key=lambda row: (
            -(int(row["year"]) if row["year"].isdigit() else 0),
            row["title"].lower(),
        ),
    )
    write_csv(
        args.output,
        candidate_rows,
        [
            "title",
            "year",
            "doi",
            "url",
            "venue",
            "authors",
            "work_type",
            "query_ids",
            "source_apis",
        ],
    )
    write_csv(
        args.log,
        logs,
        [
            "query_id",
            "source_api",
            "query",
            "request_url",
            "total_results",
            "returned_results",
            "response_sha256",
            "searched_at_utc",
        ],
    )
    print(f"Wrote {len(candidate_rows)} unique candidates to {args.output}")
    print(f"Wrote {len(logs)} search-log entries to {args.log}")


if __name__ == "__main__":
    main()
