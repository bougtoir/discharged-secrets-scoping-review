#!/usr/bin/env python3
"""Fetch public audit documents into a local, git-ignored text cache.

Only extracted plain text is cached locally for single-reviewer coding; no
copyrighted full text is committed. The committed audit records keep short
quotations or precise locators, per the codebook.
"""

from __future__ import annotations

import csv
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".doc_cache"
SEEDS = ROOT / "public_document_seeds.csv"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/125.0 Safari/537.36")


def slug(org: str, title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", f"{org}-{title}".lower()).strip("-")[:80]


def html_to_text(raw: bytes) -> str:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n"))


def pdf_to_text(raw: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as fh:
        fh.write(raw)
        fh.flush()
        out = subprocess.run(["pdftotext", "-q", fh.name, "-"],
                             capture_output=True)
    return out.stdout.decode("utf-8", "replace")


def fetch(url: str) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "en;q=0.9",
    })
    with urllib.request.urlopen(request, timeout=45) as resp:
        raw = resp.read(25 * 1024 * 1024)
        ctype = resp.headers.get("Content-Type", "")
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        return pdf_to_text(raw), "pdf"
    return html_to_text(raw), "html"


def main() -> None:
    CACHE.mkdir(exist_ok=True)
    with SEEDS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    ok = 0
    for row in rows:
        name = slug(row["organization"], row["title"])
        target = CACHE / f"{name}.txt"
        try:
            text, kind = fetch(row["url"])
            target.write_text(text, encoding="utf-8")
            ok += 1
            print(f"OK   {kind:4} {len(text):>8} {name}")
        except Exception as error:  # noqa: BLE001 - report and continue
            print(f"FAIL       {type(error).__name__}: {str(error)[:80]} {name}")
    print(f"cached {ok}/{len(rows)} documents in {CACHE}")


if __name__ == "__main__":
    main()
