#!/usr/bin/env python3
"""Import MITRE ATT&CK for ICS techniques (IDs and names only) for validating links.

Reads  sources/attack-ics/v<ver>/ics-attack.json (pristine, sha256-checked)
Writes data/attack-ics/v<ver>/techniques.json

Only technique IDs, names, tactics and URLs are kept. Revoked techniques are
listed with their replacements so the build can say what an old ID became.
"""
from __future__ import annotations

import argparse

from common import ATTACK_ICS_RE, ATTACK_ICS_VERSION, DATA, SOURCES, load_json, rel, verify_provenance, write_json


def ext_ref(obj):
    for r in obj.get("external_references", []):
        if r.get("source_name") == "mitre-attack":
            return r.get("external_id"), r.get("url")
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", default=ATTACK_ICS_VERSION)
    args = ap.parse_args()

    src_dir = SOURCES / "attack-ics" / f"v{args.version}"
    prov = verify_provenance(src_dir)
    bundle = load_json(src_dir / prov["file"])
    objs = bundle["objects"]
    by_stix = {o["id"]: o for o in objs}

    collection = next(o for o in objs if o["type"] == "x-mitre-collection")
    if collection.get("x_mitre_version") != args.version:
        raise SystemExit(f"collection version {collection.get('x_mitre_version')} != {args.version}")

    techniques, revoked, deprecated = [], {}, []
    for o in objs:
        if o["type"] != "attack-pattern":
            continue
        tid, url = ext_ref(o)
        if not tid:
            continue
        if not ATTACK_ICS_RE.match(tid):
            raise SystemExit(f"unexpected ATT&CK id {tid}")
        if o.get("revoked"):
            revoked[tid] = None
            continue
        if o.get("x_mitre_deprecated"):
            deprecated.append(tid)
            continue
        techniques.append({
            "id": tid,
            "name": o["name"],
            "subtechnique": bool(o.get("x_mitre_is_subtechnique")),
            "tactics": sorted(p["phase_name"] for p in o.get("kill_chain_phases", [])),
            "url": url,
        })

    # revoked-by relationships point old -> new
    for o in objs:
        if o["type"] == "relationship" and o.get("relationship_type") == "revoked-by":
            old_id, _ = ext_ref(by_stix.get(o["source_ref"], {}))
            new_id, _ = ext_ref(by_stix.get(o["target_ref"], {}))
            if old_id in revoked:
                revoked[old_id] = new_id

    techniques.sort(key=lambda t: t["id"])
    out = DATA / "attack-ics" / f"v{args.version}" / "techniques.json"
    write_json(out, {
        "source": prov["source"],
        "version": args.version,
        "collection_modified": collection.get("modified"),
        "notice": "© 2026 The MITRE Corporation. This work is reproduced and distributed with the permission of The MITRE Corporation.",
        "techniques": techniques,
        "revoked": dict(sorted(revoked.items())),
        "deprecated": sorted(deprecated),
    })
    print(f"ATT&CK for ICS v{args.version}: {len(techniques)} active techniques, "
          f"{len(revoked)} revoked, {len(deprecated)} deprecated -> {rel(out)}")


if __name__ == "__main__":
    main()
