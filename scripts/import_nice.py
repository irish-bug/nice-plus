#!/usr/bin/env python3
"""Import the official NICE Framework Components JSON into the nice-plus model.

Reads  sources/nice/v<ver>/<file>.json (pristine, sha256-checked)
Writes data/nice/v<ver>/{framework,categories,work_roles,competency_areas,
       statements,role_statements,competency_statements}.json

Statement text is kept exactly as published (including stray whitespace).
NICE does not mark statements as core or additional for a role, so every
NICE role link gets flag "unspecified".
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict

from common import (DATA, NICE_ROLE_RE, NICE_STATEMENT_RE, NICE_VERSION, SOURCES,
                    load_json, rel, verify_provenance, write_json)

STATEMENT_TYPES = {"task", "knowledge", "skill"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", default=NICE_VERSION)
    args = ap.parse_args()

    src_dir = SOURCES / "nice" / f"v{args.version}"
    prov = verify_provenance(src_dir)
    raw = load_json(src_dir / prov["file"])
    source_id = prov["source"]
    doc = raw["documents"][0]
    if doc["version"] != args.version:
        raise SystemExit(f"document says version {doc['version']}, expected {args.version}")

    elements = {e["element_identifier"]: e for e in raw["elements"]}
    by_type = defaultdict(list)
    for e in raw["elements"]:
        by_type[e["element_type"]].append(e)

    links = defaultdict(list)  # source element -> [dest element ids], in published order
    for r in raw["relationships"]:
        if r["relationship_identifier"] != "projection":
            raise SystemExit(f"unexpected relationship type {r['relationship_identifier']}")
        links[r["source_element_identifier"]].append(r["dest_element_identifier"])

    def cite(eid: str) -> list[dict]:
        return [{"source": source_id, "locator": eid, "locator_status": "verified", "support": "verbatim"}]

    # Statements
    statements = []
    for t in ("task", "knowledge", "skill"):
        for e in sorted(by_type[t], key=lambda e: e["element_identifier"]):
            sid = e["element_identifier"]
            if not NICE_STATEMENT_RE.match(sid):
                raise SystemExit(f"NICE statement id {sid!r} does not match {NICE_STATEMENT_RE.pattern}")
            statements.append({
                "id": sid,
                "type": t,
                "text": e["text"],
                "source": "nice",
                "nice_version": args.version,
                "status": "official",
                "citations": cite(sid),
            })
    statement_ids = {s["id"] for s in statements}

    # Categories and work roles
    role_category = {}
    categories = []
    for e in sorted(by_type["category"], key=lambda e: e["element_identifier"]):
        cid = e["element_identifier"]
        roles = [d for d in links[cid] if elements.get(d, {}).get("element_type") == "work_role"]
        for rid in roles:
            role_category[rid] = cid
        categories.append({"id": cid, "title": e["title"], "description": e["text"],
                           "work_roles": sorted(roles), "nice_version": args.version})

    work_roles, role_statements = [], []
    for e in sorted(by_type["work_role"], key=lambda e: e["element_identifier"]):
        rid = e["element_identifier"]
        if not NICE_ROLE_RE.match(rid):
            raise SystemExit(f"NICE work role id {rid!r} does not match {NICE_ROLE_RE.pattern}")
        dests = links[rid]
        opm = sorted(d for d in dests if elements.get(d, {}).get("element_type") == "opm_code")
        stmts = [d for d in dests if d in statement_ids]
        work_roles.append({
            "id": rid,
            "title": e["title"],
            "description": e["text"],
            "category": role_category.get(rid),
            "source": "nice",
            "status": "official",
            "nice_version": args.version,
            "extends": [],
            "overlaps": [],
            "opm_codes": opm,
            "citations": cite(rid),
        })
        for sid in sorted(stmts):
            role_statements.append({"role": rid, "statement": sid, "flag": "unspecified",
                                    "basis": "nice-published", "via": None, "rationale": None})

    competency_areas, competency_statements = [], []
    for e in sorted(by_type["competency_area"], key=lambda e: e["element_identifier"]):
        caid = e["element_identifier"]
        stmts = sorted(d for d in links[caid] if d in statement_ids)
        competency_areas.append({"id": caid, "title": e["title"], "description": e["text"],
                                 "statement_count": len(stmts), "nice_version": args.version})
        competency_statements += [{"competency_area": caid, "statement": s} for s in stmts]

    linked = {rs["statement"] for rs in role_statements}
    orphans = sorted(statement_ids - linked)

    framework = {
        "source": source_id,
        "name": doc["name"],
        "doc_identifier": doc["doc_identifier"],
        "version": args.version,
        "released": prov["released"],
        "released_source": prov["released_source"],
        "retrieved": prov["retrieved"],
        "sha256": prov["sha256"],
        "counts": {
            "work_roles": len(work_roles),
            "statements": dict(Counter(s["type"] for s in statements)),
            "role_statement_links": len(role_statements),
            "competency_areas": len(competency_areas),
        },
        "observations": {
            "statements_in_no_work_role": orphans,
            "competency_areas_without_statements": [c["id"] for c in competency_areas if c["statement_count"] == 0],
        },
    }

    out = DATA / "nice" / f"v{args.version}"
    write_json(out / "framework.json", framework)
    write_json(out / "categories.json", categories)
    write_json(out / "work_roles.json", work_roles)
    write_json(out / "statements.json", statements)
    write_json(out / "role_statements.json", role_statements)
    write_json(out / "competency_areas.json", competency_areas)
    write_json(out / "competency_statements.json", competency_statements)
    print(f"NICE v{args.version}: {len(work_roles)} roles, {len(statements)} statements, "
          f"{len(role_statements)} role links, {len(orphans)} statements in no role -> {rel(out)}/")


if __name__ == "__main__":
    main()
