"""Shared paths, ID rules and JSON helpers for the nice-plus scripts."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
DATA = ROOT / "data"
PLUS = ROOT / "plus"
EXPORT = ROOT / "export"
SCHEMA = ROOT / "schema"

NICE_VERSION = "2.2.0"
ATTACK_ICS_VERSION = "20.1"
EXPORT_SCHEMA_VERSION = "0.3.0"

# Each namespace has its own ID pattern. A plus ID can never match a NICE ID
# pattern and vice versa, so they cannot collide. ATT&CK for ICS technique IDs
# (T0800-T0899, T16xx) look like NICE task IDs, so they only ever appear in
# `attack_ics` fields, never as statement IDs.
NICE_STATEMENT_RE = re.compile(r"^[TKS]\d{4}$")
NICE_ROLE_RE = re.compile(r"^(OG|DD|IO|PD|IN)-WRL-\d{3}$")
PLUS_STATEMENT_RE = re.compile(r"^P[TKS]-OT-\d{4}$")
PLUS_ROLE_RE = re.compile(r"^PR-OT-\d{3}$")
ATTACK_ICS_RE = re.compile(r"^T\d{4}(\.\d{3})?$")

TYPE_BY_LETTER = {"T": "task", "K": "knowledge", "S": "skill"}


def statement_type_from_id(sid: str) -> str:
    """Type implied by a NICE (T0001) or plus (PT-OT-0001) statement ID."""
    if NICE_STATEMENT_RE.match(sid):
        return TYPE_BY_LETTER[sid[0]]
    if PLUS_STATEMENT_RE.match(sid):
        return TYPE_BY_LETTER[sid[1]]
    raise ValueError(f"not a statement id: {sid!r}")


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj) -> None:
    """Write stable, diff-friendly JSON (2-space indent, UTF-8, trailing newline)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_provenance(src_dir: Path) -> dict:
    """Check a pristine source file against its provenance.json sha256."""
    prov = load_json(src_dir / "provenance.json")
    actual = sha256_file(src_dir / prov["file"])
    if actual != prov["sha256"]:
        sys.exit(f"{src_dir / prov['file']}: sha256 {actual} does not match provenance {prov['sha256']}")
    return prov


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))
