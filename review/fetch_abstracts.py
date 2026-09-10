#!/usr/bin/env python3
"""Fetch abstracts and metadata for screening candidates from OpenAlex.

Abstracts are reconstructed from OpenAlex inverted indexes and written to a
local cache used only for single-reviewer screening. The cache is not part of
the reproducible public dataset (abstracts remain the publishers' copyright);
only screening decisions and coded reasons are published.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

OPENALEX = "https://api.openalex.org/works"
MAILTO = "discharged-secrets-audit@example.org"


def normalized_doi(value: str) -> str:
    doi = value.strip().lower()
    if doi.startswith("http"):
        doi = doi.split("doi.org/", 1)[-1]
    return doi


def reconstruct_abstract(inverted: dict | None) -> str:
    if not inverted:
        return ""
    positions: list[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for idx in idxs:
            positions.append((idx, word))
    positions.sort()
    return " ".join(word for _, word in positions)


def fetch_batch(dois: list[str]) -> dict[str, dict]:
    joined = "|".join(f"https://doi.org/{d}" for d in dois)
    params = {
        "filter": f"doi:{joined}",
        "per-page": str(len(dois)),
        "select": "doi,title,publication_year,type,abstract_inverted_index",
        "mailto": MAILTO,
    }
    url = f"{OPENALEX}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": f"discharged-secrets-audit ({MAILTO})"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.load(resp)
    out: dict[str, dict] = {}
    for work in payload.get("results", []):
        doi = normalized_doi(work.get("doi") or "")
        if not doi:
            continue
        out[doi] = {
            "title": work.get("title") or "",
            "year": work.get("publication_year") or "",
            "type": work.get("type") or "",
            "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("review/candidates.csv"))
    parser.add_argument("--cache", type=Path, default=Path("review/.abstract_cache.csv"))
    parser.add_argument("--batch", type=int, default=40)
    args = parser.parse_args()

    with args.candidates.open(newline="", encoding="utf-8") as handle:
        candidates = list(csv.DictReader(handle))

    cached: dict[str, dict] = {}
    if args.cache.exists():
        with args.cache.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                cached[row["doi"]] = row

    dois = []
    seen = set()
    for row in candidates:
        doi = normalized_doi(row.get("doi", ""))
        if doi and doi not in cached and doi not in seen:
            dois.append(doi)
            seen.add(doi)

    print(f"candidates={len(candidates)} cached={len(cached)} to_fetch={len(dois)}")
    fetched = 0
    for i in range(0, len(dois), args.batch):
        batch = dois[i : i + args.batch]
        for attempt in range(4):
            try:
                result = fetch_batch(batch)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"  batch {i} attempt {attempt} failed: {exc}")
                time.sleep(3 * (attempt + 1))
        else:
            result = {}
        for doi in batch:
            info = result.get(doi, {"title": "", "year": "", "type": "", "abstract": ""})
            cached[doi] = {"doi": doi, **info}
        fetched += len(batch)
        if (i // args.batch) % 5 == 0:
            print(f"  fetched {fetched}/{len(dois)}")
        time.sleep(0.2)

    fieldnames = ["doi", "title", "year", "type", "abstract"]
    args.cache.parent.mkdir(parents=True, exist_ok=True)
    with args.cache.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for doi in sorted(cached):
            row = cached[doi]
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    with_abs = sum(1 for r in cached.values() if r.get("abstract"))
    print(f"cache rows={len(cached)} with_abstract={with_abs}")


if __name__ == "__main__":
    main()
