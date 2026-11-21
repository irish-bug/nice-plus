#!/usr/bin/env python3
"""Import Cyber Fire OT puzzle KSA tags as an example coverage collection.

Reads  <repo>/categories/*/*/puzzle.md front matter (default repo:
       ../cyberfire/operationaltechnology, the puzzles repository that the
       ot1 repo pins as its `puzzles` submodule)
Writes data/coverage/cyberfire-operationaltechnology.json

Only `ksas`, `objective` and `params.release-id` are kept. Answers, hints,
authors and puzzle text are dropped immediately and never written anywhere.
KSA tags are author-assigned, so coverage provenance is "author-tagged".
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml  # PyYAML; see requirements.txt

from common import DATA, NICE_STATEMENT_RE, ROOT, rel, write_json

COLLECTION_ID = "cyberfire-operationaltechnology"
DEFAULT_REPO = ROOT.parent / "cyberfire" / "operationaltechnology"


def git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = yaml.safe_load(text[3:end]) or {}
    return data if isinstance(data, dict) else {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    args = ap.parse_args()
    repo = args.repo.resolve()
    cats = repo / "categories"
    if not cats.is_dir():
        raise SystemExit(f"{cats} not found; pass --repo")

    modules, untagged, bad_ids = [], [], []
    for p in sorted(cats.glob("*/*/puzzle.md")):
        fm = front_matter(p)
        puzzle = p.parent.relative_to(cats).as_posix()  # e.g. "ot-core/14"
        ksas = [str(k).strip() for k in (fm.get("ksas") or [])]
        objective = fm.get("objective")
        release = (fm.get("params") or {}).get("release-id")
        fm.clear()  # drop answers and everything else straight away
        if not ksas:
            untagged.append(puzzle)
            continue
        for k in ksas:
            if not NICE_STATEMENT_RE.match(k):
                bad_ids.append(f"{puzzle}: {k}")
        modules.append({
            "id": f"{COLLECTION_ID}:{puzzle}",
            "collection": COLLECTION_ID,
            "path": f"categories/{puzzle}/puzzle.md",
            "category": puzzle.split("/")[0],
            "objective": str(objective) if objective is not None else None,
            "release_id": release,
            "statements": sorted(set(ksas), key=ksas.index),
            "provenance": "author-tagged",
        })
    if bad_ids:
        raise SystemExit("KSA tags that are not NICE statement IDs:\n  " + "\n  ".join(bad_ids))

    out = DATA / "coverage" / f"{COLLECTION_ID}.json"
    write_json(out, {
        "collection": {
            "id": COLLECTION_ID,
            "title": "Cyber Fire OT puzzles",
            "source": COLLECTION_ID,
            "role": "example coverage source",
            "repository": repo.name,  # the remote URL is a private server, so only the name is recorded
            "commit": git(repo, "rev-parse", "HEAD"),
            "commit_date": git(repo, "log", "-1", "--format=%cs"),
            "tag_scheme": "NICE statement IDs in puzzle.md front matter `ksas:`",
            "objective_note": "`objective` is copied as written; many are lab labels, not learning objectives.",
        },
        "modules": modules,
        "untagged": untagged,
    })
    print(f"Cyber Fire: {len(modules)} tagged puzzles, {len(untagged)} untagged, "
          f"{len({s for m in modules for s in m['statements']})} distinct NICE IDs -> {rel(out)}")


if __name__ == "__main__":
    main()
