#!/usr/bin/env python3
"""
Upload the reorganized "paperless" archive into a paperless-ngx instance.

Folder layout expected (built by the earlier reorganization step):
    paperless/YEAR/PERSON/COMPANY/DOCTYPE/YYYYMMDD_COMPANY_DESC_PERSON_DOCTYPE.pdf

Mapping applied:
    correspondent  = COMPANY    (skipped if "none")
    document_type  = DOCTYPE
    tags           = [PERSON]   (skipped if "none")
    title          = DESC, split into words at CamelCase boundaries
    created        = date parsed from the filename (skipped if "ongedateerd")

Usage:
    pip install requests
    python3 upload_to_paperless.py --root /path/to/Organized/paperless \
        --url https://pl.brnb.nl --token YOUR_TOKEN

Useful flags:
    --dry-run        Show what would be uploaded/created without calling the API
    --limit N        Only process the first N files (good for a test run)
    --state FILE     Path to the resume-state JSON (default: ./upload_state.json)

The script is resumable: every file it successfully submits is recorded in the
state file by relative path, and reruns skip anything already recorded there.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

try:
    import requests
except ImportError:
    sys.exit("This script needs the 'requests' package: pip install requests")


def humanize(desc: str) -> str:
    """Turn 'FactuurWinterjas' into 'Factuur Winterjas'."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", desc)
    s = re.sub(r"(?<=[A-Za-z])(?=[0-9])", " ", s)
    return s.strip()


def parse_date(date_str: str):
    if date_str == "ongedateerd":
        return None
    try:
        return datetime.strptime(date_str, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


class PaperlessClient:
    def __init__(self, base_url: str, token: str, dry_run: bool = False):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {token}"})
        self.dry_run = dry_run
        self._correspondents = {}
        self._tags = {}
        self._document_types = {}

    def _get_or_create(self, cache: dict, endpoint: str, name: str) -> int:
        key = name.lower()
        if key in cache:
            return cache[key]

        resp = self.session.get(
            f"{self.base}/api/{endpoint}/",
            params={"name__iexact": name, "page_size": 1},
            timeout=30,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            obj_id = results[0]["id"]
        else:
            if self.dry_run:
                # fabricate a negative placeholder id in dry-run mode
                obj_id = -(len(cache) + 1)
            else:
                create_resp = self.session.post(
                    f"{self.base}/api/{endpoint}/", json={"name": name}, timeout=30
                )
                create_resp.raise_for_status()
                obj_id = create_resp.json()["id"]
        cache[key] = obj_id
        return obj_id

    def correspondent_id(self, name: str) -> int:
        return self._get_or_create(self._correspondents, "correspondents", name)

    def tag_id(self, name: str) -> int:
        return self._get_or_create(self._tags, "tags", name)

    def document_type_id(self, name: str) -> int:
        return self._get_or_create(self._document_types, "document_types", name)

    def upload(self, filepath: str, title: str, correspondent: str,
               document_type: str, tags: list, created: str):
        data = {"title": title}
        if created:
            data["created"] = created
        if correspondent:
            data["correspondent"] = str(self.correspondent_id(correspondent))
        if document_type:
            data["document_type"] = str(self.document_type_id(document_type))
        tag_ids = [str(self.tag_id(t)) for t in tags if t]

        if self.dry_run:
            return {"dry_run": True, "title": title, "correspondent": correspondent,
                     "document_type": document_type, "tags": tags, "created": created}

        with open(filepath, "rb") as fh:
            files = {"document": (os.path.basename(filepath), fh, "application/pdf")}
            form = list(data.items()) + [("tags", t) for t in tag_ids]
            resp = self.session.post(
                f"{self.base}/api/documents/post_document/",
                data=form, files=files, timeout=120,
            )
        resp.raise_for_status()
        return resp.text.strip().strip('"')  # task UUID


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to the paperless/ folder")
    ap.add_argument("--url", required=True, help="paperless-ngx base URL")
    ap.add_argument("--token", required=True, help="paperless-ngx API token")
    ap.add_argument("--state", default="upload_state.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=0.3,
                     help="Seconds to wait between uploads")
    args = ap.parse_args()

    if os.path.exists(args.state):
        with open(args.state) as f:
            state = json.load(f)
    else:
        state = {}

    client = PaperlessClient(args.url, args.token, dry_run=args.dry_run)

    files = []
    for dirpath, _, filenames in os.walk(args.root):
        for fn in filenames:
            if fn.lower().endswith(".pdf"):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    total = len(files)
    done = skipped = failed = 0

    for filepath in files:
        rel = os.path.relpath(filepath, args.root)
        if rel in state:
            skipped += 1
            continue
        if args.limit and done >= args.limit:
            break

        base = os.path.basename(filepath)[:-4]
        try:
            date_str, company, desc, person, doctag = base.split("_")
        except ValueError:
            print(f"SKIP (unexpected filename format): {rel}")
            failed += 1
            continue

        title = humanize(desc)
        created = parse_date(date_str)
        correspondent = None if company == "none" else company
        document_type = None if doctag == "none" else doctag
        tags = [t for t in (person,) if t != "none"]

        try:
            result = client.upload(filepath, title, correspondent, document_type,
                                    tags, created)
            state[rel] = {"result": result, "ts": datetime.now().isoformat()}
            done += 1
            print(f"OK  [{done}/{total - skipped}] {rel} -> {result}")
        except Exception as e:
            failed += 1
            print(f"FAIL {rel}: {e}")

        if not args.dry_run:
            with open(args.state, "w") as f:
                json.dump(state, f, indent=2)
            time.sleep(args.sleep)

    print(f"\nDone. uploaded={done} skipped(already done)={skipped} failed={failed} total={total}")


if __name__ == "__main__":
    main()