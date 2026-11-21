#!/usr/bin/env python3
"""Validate data and exports against the JSON Schemas (needs `jsonschema`).

build.py already enforces the model's rules with the standard library; this
is an extra check that the files match the published schemas.
"""
from __future__ import annotations

import sys

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    sys.exit("check_schema.py needs jsonschema>=4.18: pip install -r requirements-dev.txt")

from common import DATA, EXPORT, NICE_VERSION, PLUS, SCHEMA, SOURCES, load_json, rel

model = load_json(SCHEMA / "nice-plus.schema.json")
export_schema = load_json(SCHEMA / "role-export.schema.json")
registry = Registry().with_resources([
    (model["$id"], Resource.from_contents(model)),
    ("nice-plus.schema.json", Resource.from_contents(model)),
    (export_schema["$id"], Resource.from_contents(export_schema)),
])


def validator(defname: str | None = None):
    schema = export_schema if defname is None else {"$ref": f"{model['$id']}#/$defs/{defname}"}
    return Draft202012Validator(schema, registry=registry)


def check(label: str, v, items) -> int:
    n = 0
    for i, item in enumerate(items):
        for e in v.iter_errors(item):
            n += 1
            print(f"{label}[{i}] {'/'.join(map(str, e.absolute_path))}: {e.message}")
    print(f"{label}: {len(items)} checked, {n} errors")
    return n


errors = 0
nice = DATA / "nice" / f"v{NICE_VERSION}"
errors += check(rel(nice / "statements.json"), validator("statement"), load_json(nice / "statements.json"))
errors += check(rel(nice / "work_roles.json"), validator("workRole"), load_json(nice / "work_roles.json"))
errors += check(rel(nice / "role_statements.json"), validator("roleStatement"), load_json(nice / "role_statements.json"))
plus = [dict(s, source="plus", status="draft") for s in load_json(PLUS / "statements.json")["statements"]]
errors += check(rel(PLUS / "statements.json"), validator("statement"), plus)
errors += check(rel(SOURCES / "registry.json"), validator("source"), load_json(SOURCES / "registry.json")["sources"])
if (PLUS / "competency_areas.json").exists():
    errors += check(rel(PLUS / "competency_areas.json"), validator("competencyArea"),
                    load_json(PLUS / "competency_areas.json")["competency_areas"])
for p in sorted((DATA / "coverage").glob("*.json")):
    errors += check(rel(p), validator("module"), load_json(p)["modules"])
for p in sorted((EXPORT / "roles").glob("*.json")):
    errors += check(rel(p), validator(), [load_json(p)])
sys.exit(1 if errors else 0)
