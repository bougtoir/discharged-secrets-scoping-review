#!/usr/bin/env python3
"""Bounded supplementary operator-document search (see
``audit/SUPPLEMENTARY_SEARCH_PROTOCOL.md``).

Fetches, per sampled operator domain: the well-known security.txt locations,
the homepage, and up to 8 same-domain links matching governance keywords.
Every fetched document is saved verbatim under ``data/raw/operator_docs/``
and logged in ``data/document_search_ledger.csv``; coding results go to
``results/supplementary_document_search.csv``.

Usage: python3 audit/supplementary_document_search.py
"""

import csv
import hashlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "operator_docs"
LEDGER = ROOT / "data" / "document_search_ledger.csv"
OUT = ROOT / "results" / "supplementary_document_search.csv"
SAMPLE = ROOT / "audit" / "operator_sample.csv"

LINK_RX = re.compile(
    r"privacy|terms|legal|security|vulnerab|disclos|responsible|sustainab|"
    r"recycl|return|imprint|policy|cookie|data", re.I)
VULN_RX = re.compile(
    r"vulnerabilit|responsible[- ]disclosure|coordinated[- ]disclosure|"
    r"bug[- ]bounty|report.{0,40}security|security@", re.I | re.S)
EOL_RX = re.compile(
    r"recycl|end[- ]of[- ]life|second[- ]life|dispos|"
    r"return.{0,60}(vehicle|scooter|bike|device|battery)|take[- ]back",
    re.I | re.S)
TAG_RX = re.compile(r"<[^>]+>")
WS_RX = re.compile(r"\s+")

UA = {"User-Agent": "Mozilla/5.0 (compatible; academic-audit; +https://github.com/bougtoir/discharged-secrets-scoping-review)"}
TIMEOUT = 20
MAX_LINKS = 8
MAX_REQ = 25


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []  # (href, anchor_text)
        self._href = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._buf)))
            self._href = None

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)


def fetch(url: str):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read(2_000_000)
            return resp.status, resp.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, b""
    except Exception as e:
        return f"error:{type(e).__name__}", url, b""


def save(domain: str, url: str, body: bytes, seq: int) -> Path:
    d = RAW / domain
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{seq:02d}.html"
    p.write_bytes(body)
    return p


def strip_html(body: bytes) -> str:
    try:
        text = body.decode("utf-8", "replace")
    except Exception:
        return ""
    return WS_RX.sub(" ", TAG_RX.sub(" ", text))


def snippet(text: str, m: re.Match) -> str:
    s = max(0, m.start() - 80)
    return text[s:m.end() + 80].strip()[:240]


def main() -> None:
    sample = list(csv.DictReader(SAMPLE.open(encoding="utf-8")))
    ledger_rows = []
    out_rows = []
    for s in sample:
        dom = s["operator_domain"]
        seq = 0
        fetched = []  # (url, text)
        requests = 0

        def go(url, doc_type):
            nonlocal seq, requests
            if requests >= MAX_REQ:
                return None
            requests += 1
            status, final_url, body = fetch(url)
            path = ""
            if body:
                seq += 1
                path = str(save(dom, final_url, body, seq).relative_to(ROOT))
            ledger_rows.append({
                "operator_domain": dom, "url": url, "final_url": final_url,
                "doc_type": doc_type, "http_status": status,
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "bytes": str(len(body)),
                "sha256": hashlib.sha256(body).hexdigest() if body else "",
                "path": path,
            })
            return body

        # security.txt endpoints
        sec_well = go(f"https://{dom}/.well-known/security.txt", "security_txt_wellknown")
        if not sec_well:
            sec_well = go(f"https://{dom}/security.txt", "security_txt_root")
        if sec_well:
            fetched.append((f"security.txt:{dom}", sec_well.decode("utf-8", "replace")))

        # homepage + bounded link crawl
        home = go(f"https://{dom}/", "homepage")
        if not home:
            home = go(f"http://{dom}/", "homepage_http")
        links = []
        if home:
            text = strip_html(home)
            fetched.append((f"https://{dom}/", text))
            lp = LinkParser()
            try:
                lp.feed(home.decode("utf-8", "replace"))
            except Exception:
                pass
            seen = set()
            for href, anchor in lp.links:
                u = urllib.parse.urljoin(f"https://{dom}/", href)
                pu = urllib.parse.urlparse(u)
                if pu.scheme not in ("http", "https"):
                    continue
                host = pu.netloc.lower().split(":")[0]
                base = dom.lower().replace("www.", "")
                if not (host.endswith(base) or base.endswith(host.replace("www.", ""))):
                    continue
                cand = pu.path + " " + anchor
                if LINK_RX.search(cand) and u not in seen:
                    seen.add(u)
                    links.append((u, "linked_document"))
                if len(links) >= MAX_LINKS:
                    break
        for url, dt in links:
            body = go(url, dt)
            if body:
                fetched.append((url, strip_html(body)))

        # coding
        vuln_url = vuln_snip = ""
        eol_url = eol_snip = ""
        for url, text in fetched:
            m = VULN_RX.search(text)
            if m and not vuln_url:
                vuln_url, vuln_snip = url, snippet(text, m)
            m2 = EOL_RX.search(text)
            if m2 and not eol_url:
                eol_url, eol_snip = url, snippet(text, m2)
        status = "searched" if fetched else "unavailable"
        out_rows.append({
            "operator_domain": dom,
            "sample_rank": s["sample_rank"],
            "search_status": status,
            "documents_fetched": str(len(fetched)),
            "security_txt": "yes" if sec_well else "no",
            "vulnerability_channel_found": "yes" if vuln_url else "no",
            "vulnerability_channel_url": vuln_url,
            "vulnerability_channel_snippet": vuln_snip,
            "return_disposal_mention_found": "yes" if eol_url else "no",
            "return_disposal_url": eol_url,
            "return_disposal_snippet": eol_snip,
        })
        print(f"{dom}: {status}, {len(fetched)} docs, "
              f"vuln={'yes' if vuln_url else 'no'}, eol={'yes' if eol_url else 'no'}")
        time.sleep(0.5)

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ledger_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(ledger_rows)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    print(f"ledger: {LEDGER.relative_to(ROOT)} ({len(ledger_rows)} requests)")


if __name__ == "__main__":
    main()
