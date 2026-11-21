#!/usr/bin/env python3
"""Validate nice-plus data and build one export file per plus role.

Reads  data/nice, data/attack-ics, data/coverage, plus/statements.json,
       plus/roles/*.json, sources/registry.json
Writes export/roles/<role id>.json (contract: schema/role-export.schema.json)
       export/index.json

Fails (exit 1) on any rule violation: ID namespace clashes, unknown sources,
unknown or revoked ATT&CK IDs, unknown NICE statements, duplicate links.
Output is deterministic: no timestamps, stable ordering.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from common import (ATTACK_ICS_VERSION, DATA, EXPORT, EXPORT_SCHEMA_VERSION, NICE_ROLE_RE,
                    NICE_STATEMENT_RE, NICE_VERSION, PLUS, PLUS_ROLE_RE, PLUS_STATEMENT_RE,
                    SOURCES, ATTACK_ICS_RE, load_json, rel, statement_type_from_id, write_json)

FLAGS = {"core", "additional"}
RELATIONS = {"refines", "complements", "extends"}
SUPPORT = {"verbatim", "paraphrase", "related"}
LOCATOR_STATUS = {"verified", "to-verify", "none"}
PURDUE = {"0", "1", "2", "3", "3.5", "4", "5"}
TYPE_ORDER = {"task": 0, "knowledge": 1, "skill": 2}
ROLE_STATUS = {"stub", "draft", "reviewed"}
PLUS_STATEMENT_STATUS = {"draft", "reviewed"}
PLUS_CA_RE = __import__("re").compile(r"^PC-OT-\d{3}$")

DRAFT_NOTICE = ("DRAFT. NICE Plus is an independent extension of the NIST NICE Framework for OT/ICS roles. "
                "It is not a NIST product and has not been reviewed or endorsed by NIST. NICE statements are "
                "quoted exactly from NICE Framework Components; plus statements (IDs starting P) are drafts "
                "authored by nice-plus.")

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def check_citations(owner: str, cits: list, registry: dict) -> None:
    if not cits:
        err(f"{owner}: no citations")
    for c in cits:
        if c.get("source") not in registry:
            err(f"{owner}: unknown source {c.get('source')!r}")
        if c.get("support") not in SUPPORT:
            err(f"{owner}: bad support {c.get('support')!r}")
        if c.get("locator_status") not in LOCATOR_STATUS:
            err(f"{owner}: bad locator_status {c.get('locator_status')!r}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--nice-version", default=NICE_VERSION)
    ap.add_argument("--attack-version", default=ATTACK_ICS_VERSION)
    args = ap.parse_args()

    registry = {s["id"]: s for s in load_json(SOURCES / "registry.json")["sources"]}
    nice_dir = DATA / "nice" / f"v{args.nice_version}"
    framework = load_json(nice_dir / "framework.json")
    nice_roles = {r["id"]: r for r in load_json(nice_dir / "work_roles.json")}
    nice_stmts = {s["id"]: s for s in load_json(nice_dir / "statements.json")}
    nice_links = defaultdict(list)
    roles_of = defaultdict(list)
    for l in load_json(nice_dir / "role_statements.json"):
        nice_links[l["role"]].append(l["statement"])
        roles_of[l["statement"]].append(l["role"])

    nice_cas = {c["id"]: c for c in load_json(nice_dir / "competency_areas.json")}
    ca_of = defaultdict(list)  # statement -> competency area ids (NICE and plus)
    for l in load_json(nice_dir / "competency_statements.json"):
        ca_of[l["statement"]].append(l["competency_area"])

    attack = load_json(DATA / "attack-ics" / f"v{args.attack_version}" / "techniques.json")
    techniques = {t["id"]: t for t in attack["techniques"]}

    # Coverage collections (every file in data/coverage)
    collections, covered_by = [], defaultdict(list)
    for p in sorted((DATA / "coverage").glob("*.json")):
        c = load_json(p)
        collections.append(c)
        for m in c["modules"]:
            for sid in m["statements"]:
                covered_by[sid].append({"module": m["id"], "provenance": m["provenance"]})
    # Inferred coverage mappings for plus statements, if any (plus/coverage_map.json)
    cmap_path = PLUS / "coverage_map.json"
    module_ids = {m["id"] for c in collections for m in c["modules"]}
    if cmap_path.exists():
        for e in load_json(cmap_path).get("mappings", []):
            if e["module"] not in module_ids:
                err(f"coverage_map: unknown module {e['module']}")
            covered_by[e["statement"]].append({"module": e["module"], "provenance": "inferred",
                                               "rationale": e.get("rationale")})

    # Plus statements
    plus_stmts = {}
    for s in load_json(PLUS / "statements.json")["statements"]:
        sid = s["id"]
        if not PLUS_STATEMENT_RE.match(sid):
            err(f"{sid}: plus statement id must match {PLUS_STATEMENT_RE.pattern}")
            continue
        if NICE_STATEMENT_RE.match(sid) or sid in nice_stmts:
            err(f"{sid}: collides with the NICE namespace")
        if sid in plus_stmts:
            err(f"{sid}: duplicate plus statement")
        if s["type"] != statement_type_from_id(sid):
            err(f"{sid}: type {s['type']} does not match id prefix")
        for r in s.get("relates_to_nice", []):
            if r["id"] not in nice_stmts:
                err(f"{sid}: relates_to_nice {r['id']} is not a NICE v{args.nice_version} statement")
            if r["relation"] not in RELATIONS:
                err(f"{sid}: bad relation {r['relation']}")
        for t in s.get("attack_ics", []):
            if not ATTACK_ICS_RE.match(t):
                err(f"{sid}: bad ATT&CK id {t}")
            elif t not in techniques:
                new = attack["revoked"].get(t)
                err(f"{sid}: ATT&CK {t} is not an active technique in v{args.attack_version}"
                    + (f" (revoked; now {new})" if new else ""))
        for lvl in s.get("ot_context", {}).get("purdue_levels", []):
            if lvl not in PURDUE:
                err(f"{sid}: bad Purdue level {lvl}")
        if s.get("status", "draft") not in PLUS_STATEMENT_STATUS:
            err(f"{sid}: status must be one of {sorted(PLUS_STATEMENT_STATUS)}")
        check_citations(sid, s.get("citations", []), registry)
        plus_stmts[sid] = s

    # Plus competency areas (plus/competency_areas.json)
    plus_cas = []
    ca_path = PLUS / "competency_areas.json"
    if ca_path.exists():
        for ca in load_json(ca_path)["competency_areas"]:
            cid = ca["id"]
            if not PLUS_CA_RE.match(cid) or cid in nice_cas:
                err(f"{cid}: plus competency area id must match {PLUS_CA_RE.pattern}")
            if ca.get("status") not in {"draft", "reviewed"}:
                err(f"{cid}: bad status {ca.get('status')}")
            check_citations(cid, ca.get("citations", []), registry)
            members = list(ca.get("statements", []))
            for g in ca.get("groups", []):
                check_citations(f"{cid} / {g['title']}", g.get("citations", []), registry)
                members += g["statements"]
            for sid in members:
                if sid not in nice_stmts and sid not in plus_stmts:
                    err(f"{cid}: unknown statement {sid}")
            for sid in dict.fromkeys(members):
                ca_of[sid].append(cid)
            plus_cas.append(ca)

    # Plus roles
    exports, used_plus = [], set()
    for rp in sorted((PLUS / "roles").glob("*.json")):
        role = load_json(rp)
        rid = role["id"]
        if not PLUS_ROLE_RE.match(rid) or NICE_ROLE_RE.match(rid):
            err(f"{rp.name}: role id {rid} must match {PLUS_ROLE_RE.pattern}")
        if role["category"] not in {c for c in ("OG", "DD", "IO", "PD", "IN")}:
            err(f"{rid}: unknown category {role['category']}")
        if role.get("status") not in ROLE_STATUS:
            err(f"{rid}: status must be one of {sorted(ROLE_STATUS)}")
        for x in role.get("extends", []) + role.get("related", []):
            if x not in nice_roles:
                err(f"{rid}: unknown NICE role {x}")
        if role.get("status") == "stub" and (role.get("inherit") or role.get("add_nice") or role.get("add_plus")):
            err(f"{rid}: a stub has no statements yet; set status to draft")
        if role.get("status") != "stub" and not (role.get("inherit") or role.get("add_nice") or role.get("add_plus")):
            err(f"{rid}: status {role.get('status')} needs statements")
        check_citations(rid, role.get("citations", []), registry)

        links: dict[str, dict] = {}

        def add(sid, flag, basis, via, rationale):
            if sid in links:
                err(f"{rid}: {sid} linked twice ({links[sid]['basis']} and {basis})")
                return
            if flag not in FLAGS:
                err(f"{rid}: {sid} bad flag {flag}")
            links[sid] = {"flag": flag, "basis": basis, "via": via, "rationale": rationale}

        for inh in role.get("inherit", []):
            src = inh["role"]
            if src not in nice_roles:
                err(f"{rid}: inherits unknown NICE role {src}")
                continue
            # default_flag applies to every statement of the parent role; the
            # `core` / `additional` lists are the exceptions to it.
            override = {}
            for flag in ("core", "additional"):
                ids = set(inh.get(flag, []))
                stray = ids - set(nice_links[src])
                if stray:
                    err(f"{rid}: '{flag}' lists statements not in {src}: {sorted(stray)}")
                if flag == inh["default_flag"] and ids:
                    err(f"{rid}: '{flag}' list repeats default_flag for {src}")
                override.update({s: flag for s in ids})
            for sid in nice_links[src]:
                add(sid, override.get(sid, inh["default_flag"]), "inherited", [src], inh.get("rationale"))
        for a in role.get("add_nice", []):
            sid = a["statement"]
            if sid not in nice_stmts:
                err(f"{rid}: add_nice {sid} is not a NICE statement")
                continue
            add(sid, a["flag"], "added-nice", sorted(roles_of[sid]), a.get("rationale"))
        for a in role.get("add_plus", []):
            sid = a["statement"]
            if sid not in plus_stmts:
                err(f"{rid}: add_plus {sid} is not a plus statement")
                continue
            add(sid, a["flag"], "plus", None, a.get("rationale"))
        used_plus.update(s for s in links if s in plus_stmts)

        # Overlap with NICE roles (computed, not judged)
        role_set = set(links)
        overlaps = []
        for nid, stmts in nice_links.items():
            shared = role_set & set(stmts)
            if shared:
                overlaps.append({"role": nid, "title": nice_roles[nid]["title"], "shared": len(shared),
                                 "of_nice_role": len(stmts),
                                 "jaccard": round(len(shared) / len(role_set | set(stmts)), 3)})
        overlaps.sort(key=lambda o: (-o["shared"], o["role"]))
        overlaps = [o for o in overlaps if o["role"] not in role.get("extends", [])][:5]

        # Statements with coverage
        out_stmts, used_sources = [], {"nist-nice-v2.2.0"}
        for sid, link in links.items():
            s = nice_stmts.get(sid) or plus_stmts[sid]
            is_plus = sid in plus_stmts
            entry = {
                "id": sid,
                "type": s["type"],
                "text": s["text"],
                "source": "plus" if is_plus else "nice",
                "nice_version": None if is_plus else args.nice_version,
                "status": s.get("status", "draft") if is_plus else "official",
                "link": link,
                "relates_to_nice": s.get("relates_to_nice", []),
                "ot_context": s.get("ot_context", {"purdue_levels": [], "sectors": [], "protocol_families": []}),
                "attack_ics": [{"id": t, "name": techniques[t]["name"]} for t in s.get("attack_ics", []) if t in techniques],
                "citations": s["citations"],
                "coverage": sorted(covered_by.get(sid, []), key=lambda c: c["module"]),
                "open_questions": s.get("open_questions", []),
                "competency_areas": sorted(set(ca_of.get(sid, []))),
            }
            used_sources.update(c["source"] for c in s["citations"])
            out_stmts.append(entry)
        out_stmts.sort(key=lambda e: (e["source"] != "nice", TYPE_ORDER[e["type"]], e["id"]))

        def tally(items):
            return {"total": len(items), "covered": sum(1 for i in items if i["coverage"])}

        by_type = {t: tally([e for e in out_stmts if e["type"] == t]) for t in ("task", "knowledge", "skill")}
        by_flag = {f: tally([e for e in out_stmts if e["link"]["flag"] == f]) for f in ("core", "additional")}
        by_source = {src: tally([e for e in out_stmts if e["source"] == src]) for src in ("nice", "plus")}
        by_basis = {b: tally([e for e in out_stmts if e["link"]["basis"] == b])
                    for b in ("inherited", "added-nice", "plus")}
        modules_used = sorted({c["module"] for e in out_stmts for c in e["coverage"]})
        module_index = {m["id"]: m for c in collections for m in c["modules"]}
        used_sources.update(c["collection"]["source"] for c in collections)

        export = {
            "schema_version": EXPORT_SCHEMA_VERSION,
            "kind": "nice-plus.role",
            "notice": DRAFT_NOTICE,
            "role": {
                "id": rid,
                "title": role["title"],
                "status": role["status"],
                "source": "plus",
                "category": role["category"],
                "description": role["description"],
                "extends": [{"role": x, "title": nice_roles[x]["title"]} for x in role.get("extends", [])],
                "related": [{"role": x, "title": nice_roles[x]["title"]} for x in role.get("related", [])],
                "overlaps": overlaps,
                "overlaps_method": "Computed: NICE roles sharing the most statements with this role, excluding the roles it extends.",
                "citations": role["citations"],
                "open_questions": role.get("open_questions", []),
            },
            "frameworks": {
                "nice": {"version": args.nice_version, "released": framework["released"], "source": framework["source"]},
                "attack_ics": {"version": args.attack_version, "source": attack["source"], "notice": attack["notice"]},
            },
            "statements": out_stmts,
            "coverage": {
                "collections": [{k: c["collection"][k] for k in ("id", "title", "role", "commit", "commit_date")}
                                for c in collections],
                "summary": {"all": tally(out_stmts), "by_type": by_type, "by_flag": by_flag,
                            "by_source": by_source, "by_basis": by_basis},
                "modules": [{"id": m, "collection": module_index[m]["collection"], "path": module_index[m]["path"],
                             "objective": module_index[m]["objective"], "release_id": module_index[m]["release_id"],
                             "statements_in_role": [s for s in module_index[m]["statements"] if s in links]}
                            for m in modules_used],
                "gaps": [e["id"] for e in out_stmts if not e["coverage"]],
                "provenance_note": "author-tagged = tag assigned by the module's author; inferred = mapping proposed by nice-plus. Neither is independently verified.",
            },
            "sources": [registry[s] for s in sorted(used_sources) if s in registry],
        }
        exports.append(export)

    unused = sorted(set(plus_stmts) - used_plus)
    if unused:
        err(f"plus statements not used by any role: {unused}")

    if errors:
        print(f"{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        sys.exit(1)

    out_dir = EXPORT / "roles"
    index = []
    for ex in exports:
        path = out_dir / f"{ex['role']['id']}.json"
        write_json(path, ex)
        s = ex["coverage"]["summary"]
        index.append({"id": ex["role"]["id"], "title": ex["role"]["title"], "status": ex["role"]["status"],
                      "file": f"roles/{ex['role']['id']}.json", "statements": s["all"]["total"],
                      "covered": s["all"]["covered"]})
        print(f"{ex['role']['id']} {ex['role']['title']}: {s['all']['total']} statements "
              f"(nice {s['by_source']['nice']['total']}, plus {s['by_source']['plus']['total']}), "
              f"{s['all']['covered']} covered -> {rel(path)}")
    def stmt_brief(sid):
        s = nice_stmts.get(sid) or plus_stmts[sid]
        return {"id": sid, "type": s["type"], "text": s["text"], "source": "plus" if sid in plus_stmts else "nice",
                "status": s.get("status", "draft") if sid in plus_stmts else "official"}
    write_json(EXPORT / "competency_areas.json", {
        "schema_version": EXPORT_SCHEMA_VERSION, "kind": "nice-plus.competency_areas", "notice": DRAFT_NOTICE,
        "competency_areas": [{
            "id": ca["id"], "title": ca["title"], "status": ca["status"], "description": ca["description"],
            "citations": ca["citations"], "open_questions": ca.get("open_questions", []),
            "statements": [stmt_brief(s) for s in ca.get("statements", [])],
            "groups": [{"title": g["title"], "citations": g["citations"],
                        "statements": [stmt_brief(s) for s in g["statements"]]} for g in ca.get("groups", [])],
        } for ca in plus_cas]})
    write_json(EXPORT / "index.json", {"schema_version": EXPORT_SCHEMA_VERSION, "kind": "nice-plus.index",
                                       "nice_version": args.nice_version, "roles": index})


if __name__ == "__main__":
    main()
