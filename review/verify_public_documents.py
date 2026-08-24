#!/usr/bin/env python3

import argparse
import csv
import hashlib
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


USER_AGENT = "DischargedSecretsDocumentAudit/0.1"
MAX_BYTES = 20 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify public-document URLs without storing copyrighted content."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def verify(url: str) -> dict[str, str]:
    result = {
        "requested_url": url,
        "final_url": "",
        "http_status": "",
        "content_type": "",
        "content_length_bytes": "",
        "response_sha256": "",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "error": "",
    }
    last_error = ""
    for attempt in range(3):
        try:
            current_url = url
            for _ in range(6):
                request = urllib.request.Request(
                    current_url,
                    headers={"User-Agent": USER_AGENT},
                )
                try:
                    with urllib.request.urlopen(request, timeout=30) as response:
                        payload = response.read(MAX_BYTES + 1)
                        if len(payload) > MAX_BYTES:
                            raise ValueError(f"response exceeds {MAX_BYTES} bytes")
                        result["final_url"] = response.geturl()
                        result["http_status"] = str(response.status)
                        result["content_type"] = response.headers.get(
                            "Content-Type",
                            "",
                        )
                        result["content_length_bytes"] = str(len(payload))
                        result["response_sha256"] = hashlib.sha256(payload).hexdigest()
                        return result
                except urllib.error.HTTPError as error:
                    if error.code not in {301, 302, 303, 307, 308}:
                        raise
                    location = error.headers.get("Location")
                    if not location:
                        raise
                    current_url = urllib.parse.urljoin(current_url, location)
            raise ValueError("too many redirects")
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            last_error = f"{type(error).__name__}: {error}"
            if attempt < 2:
                time.sleep(2**attempt)
    result["error"] = last_error[:500]
    return result


def main() -> None:
    args = parse_args()
    with args.input.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    output_rows: list[dict[str, str]] = []
    for row in rows:
        verification = verify(row["url"])
        output_rows.append(
            {
                "organization": row["organization"],
                "document_type": row["document_type"],
                "title": row["title"],
                "reason": row["reason"],
                **verification,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(output_rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(output_rows)
    successes = sum(
        row["http_status"].isdigit()
        and 200 <= int(row["http_status"]) < 300
        for row in output_rows
    )
    print(f"Verified {successes} of {len(output_rows)} URLs with HTTP 2xx")


if __name__ == "__main__":
    main()
