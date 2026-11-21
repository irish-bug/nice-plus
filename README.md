# NICE Plus

**An open extension of the NIST NICE Workforce Framework for operational technology (OT)
and industrial control system (ICS) cybersecurity roles.** Roles are general OT roles, with
manufacturing as the first sector.

> **DRAFT. Not a NIST product.** NICE Plus is an independent extension. NIST has not
> reviewed or endorsed it. NICE statements are quoted exactly from the official NICE
> Framework Components. Everything with a `P…` ID is a nice-plus draft.

NICE Plus uses NICE's structure and IDs and adds what NICE lacks for OT/ICS work, so that
training can be planned from a job role. It feeds the role-led planning path of the
ottobotto OT/ICS cyber range: **role → work role + TKS statements → learning objectives →
modules → labs → exercise**.

**This is a first attempt and it will be imperfect.** NICE does not cover OT/ICS roles well.
Nobody else has published an open extension, so we are starting one, sourcing everything,
marking what we are unsure of, and inviting people who do this work to correct it. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Help wanted: tasks for people and their agents

We would like many different people, and their AI agents, to review and extend this. You
don't need to write new content to help. Finding what is wrong is just as valuable:
- a weak citation
- a statement in the wrong role
- a NICE statement we missed
- a better source

**How to help:**
1. Pick a task below.
2. Do it yourself, or paste the prompt into your agent of choice (Claude Code, Codex,
   Copilot, Cursor, Gemini, or anything else that can read a repo).
3. Read what it produces before you submit it.
4. Submit each finding as its own issue using the templates, or send a small pull request.

Agents should read [AGENTS.md](AGENTS.md) first. The key rules:
- Only cite what you actually opened.
- Look up IDs in `data/`; don't recall them.
- Mark anything you could not verify.
- Disclose AI assistance.
- Search existing issues before opening new ones.

**Start every agent prompt with:**

> You are helping review NICE Plus (https://github.com/irish-bug/nice-plus), an open, draft extension of the NIST NICE
> Framework for OT/ICS cybersecurity roles. Clone the repo and read AGENTS.md,
> CONTRIBUTING.md and README.md, and follow their rules: only cite sources you actually
> open, look up NICE and ATT&CK IDs in data/ instead of recalling them, and say plainly
> what you could not verify. Search existing issues and pull requests before reporting
> anything. Then do this task, and give me your findings as separate draft GitHub issues
> (using the repo's issue templates) for me to review before I submit them:

**Then add one task:**

| Task | Paste after the preamble |
|---|---|
| **Review a draft role** | "Review role PR-OT-00N in plus/roles/ and export/roles/. For each statement flagged core, ask whether this job really needs it; for the role as a whole, list important duties no statement covers. Challenge the core/additional flags where you disagree." |
| **Find NICE statements we missed** | "For role PR-OT-00N, search all NICE v2.2.0 statements in data/nice/v2.2.0/statements.json for ones the role needs but does not link. Explain each in one line." |
| **Spot-check citations** | "Pick 10 citations in plus/statements.json marked verified. Open each source at the stated locator and report any that do not support the statement or point to the wrong place." |
| **Verify a to-verify citation** | "Find citations with locator_status to-verify. For any you can check against a source you can actually open, report the correct locator and whether it supports the statement." |
| **Suggest sources** | "Find public, citable sources on OT/ICS cybersecurity work roles, tasks or competencies that sources/registry.json does not include (e.g. government guidance, sector profiles, job task analyses, workforce studies). For each, give the title, publisher, date, URL, reuse terms and what it would support." |
| **Point out flaws** | "Look for problems: plus statements that duplicate each other or a NICE statement, statements that mix two ideas, wording that breaks NICE style, wrong ATT&CK links, and weaknesses in the data model or export contract." |
| **Flesh out a stub role** | "Pick a role in plus/roles/ with status stub. Propose its statements (inherited, added NICE and plus) with flags and sources, following the existing draft roles. If you write files, run make build and make check." |
| **Answer an open question** | "Pick an open_questions entry from a role or competency area and argue a position with sources." |
| **Another sector** | "Review the plus statements for a sector other than manufacturing (e.g. electric power, water, oil and gas, building automation). Which statements need sector tags or different wording, and what is missing?" |
| **Cyber-Informed Engineering** | "Review competency area PC-OT-001 in plus/competency_areas.json against the DOE National CIE Strategy and INL's CIE Implementation Guide. Are statements mapped to the right principles? Which principles are thin, and what statements would fill them?" |

## Status (2026-11-20)

| Piece | State |
|---|---|
| Data model (JSON Schema) | `schema/`; export `schema_version` 0.3.0 |
| NICE import | NICE Framework Components **v2.2.0** (released 2026-04-28) |
| ATT&CK for ICS import | **v20.1** (technique IDs and names, for validating links) |
| Cyber Fire tag import | 184 tagged puzzles, an example coverage source |
| Roles | **21**: 7 drafts with statements, 14 stubs (see [Roles](#roles)) |
| Plus statements | 62 (18 knowledge, 35 tasks, 9 skills), all DRAFT and cited |
| Competency areas | **PC-OT-001 Cyber-Informed Engineering** (12 CIE principles mapped to statements) |
| Exports | `export/roles/<id>.json` for every role, contract below |
| Coverage page, browse pages (HTML) | not started |

## Quick start

```sh
pip install -r requirements.txt   # PyYAML (only for the Cyber Fire import)
make                              # import sources, validate, build exports
make check                        # also validate against the JSON Schemas (requirements-dev.txt)
```

`make build` alone works from the committed `data/` without network access or sibling
repos. The scripts write no timestamps, so a rebuild with unchanged inputs produces
byte-identical output.

## Layout

```
sources/          pristine source copies + provenance (sha256, URL, dates); registry.json lists every citable source
  nice/v2.2.0/      official NICE Framework Components JSON, unmodified
  attack-ics/v20.1/ MITRE ATT&CK for ICS STIX bundle, unmodified (licence in sources/attack-ics/LICENSE.txt)
schema/           nice-plus.schema.json (data model), role-export.schema.json (ottobotto contract)
scripts/          import_nice.py, import_attack_ics.py, import_cyberfire.py, build.py, check_schema.py
data/             generated by importers; do not hand-edit
  nice/v2.2.0/      work_roles, statements, role_statements, categories, competency_areas, framework.json
  attack-ics/v20.1/ techniques.json (+ revoked → replacement map)
  coverage/         one file per coverage collection (modules and the statement IDs they cover)
plus/             hand-authored nice-plus content
  statements.json   plus TKS statements (DRAFT, cited)
  roles/*.json      plus work roles
  competency_areas.json  plus competency areas (e.g. PC-OT-001 Cyber-Informed Engineering)
export/           generated by build.py: index.json, competency_areas.json, roles/<role id>.json
```

## Data model

Full definitions are in `schema/nice-plus.schema.json`.

| Entity | Key fields |
|---|---|
| **work role** | `id`, `title`, `description`, `category` (NICE category code), `source` (`nice`\|`plus`), `status` (`official`\|`draft`), `nice_version`, `extends[]` (NICE roles a plus role specializes), `overlaps[]`, `opm_codes[]`, `citations[]` |
| **statement** | `id`, `type` (`task`\|`knowledge`\|`skill`), `text`, `source`, `nice_version`, `status`, `citations[]`, `relates_to_nice[]` (`refines`\|`complements`\|`extends`), `ot_context` (Purdue levels, sectors, protocol families), `attack_ics[]` |
| **role ↔ statement link** | `flag` (`core`\|`additional`\|`unspecified`), `basis` (`nice-published`\|`inherited`\|`added-nice`\|`plus`), `via` (NICE roles it comes from), `rationale` |
| **citation** | `source` (registry id), `locator`, `locator_status` (`verified`\|`to-verify`\|`none`), `support` (`verbatim`\|`paraphrase`\|`related`), `note` |
| **source** | `id`, `title`, `publisher`, `version`, `date`, `url`, `licence`, `held`, `sha256`, `retrieved` |
| **module** (coverage) | `id` (`<collection>:<path>`), `collection`, `path`, `objective`, `release_id`, `statements[]`, `provenance` (`author-tagged`\|`inferred`) |
| **competency area** (plus) | `id`, `title`, `status`, `description`, `citations[]`, `open_questions[]`, `statements[]` (whole area), `groups[]` (each with `title`, `citations[]`, `statements[]`) |

### ID rules

Each namespace has its own pattern, so NICE and plus IDs cannot collide.
`build.py` and the schema both enforce this.

| Kind | Pattern | Example |
|---|---|---|
| NICE statement | `^[TKS]\d{4}$` | `K1309` |
| NICE work role | `^(OG\|DD\|IO\|PD\|IN)-WRL-\d{3}$` | `DD-WRL-009` |
| Plus statement | `^P[TKS]-OT-\d{4}$` | `PT-OT-0001`, `PK-OT-0001`, `PS-OT-0001` |
| Plus work role | `^PR-OT-\d{3}$` | `PR-OT-001` |
| Plus competency area | `^PC-OT-\d{3}$` | `PC-OT-001` (NICE uses `NF-COM-###`) |
| ATT&CK for ICS | `^T\d{4}(\.\d{3})?$` | `T0889`, `T1692.001` |

- ATT&CK technique IDs have the same `T####` shape as NICE task IDs. That is why they
  only ever appear in `attack_ics` fields and never as statement IDs.
- `build.py` checks every ATT&CK ID against the imported v20.1 data and rejects revoked
  IDs, naming the replacement (v20 replaced several older IDs, e.g. `T0855` →
  `T1692.001`).
- Plus IDs are never reused or renumbered. A withdrawn plus statement keeps its ID.

### Rules for NICE content
- NICE statement and role text is stored exactly as published, including stray
  whitespace (e.g. `T2028` ends with a space). It is versioned by `nice_version`.
- NICE does not mark statements as core or additional, so NICE's own links are
  `unspecified`. Core/additional flags on plus roles are nice-plus judgments, and each
  has a rationale.
- Plus roles **inherit** from the NICE roles they extend at build time. A new NICE
  version therefore flows through, and `build.py` flags any override that no longer
  matches.

### Rules for plus content
- Every plus statement and role cites at least one source in `sources/registry.json`.
- `locator_status` records honestly whether we checked the locator against the source:
  - `verified`: checked against the source.
  - `to-verify`: not yet checked (this includes every ISA/IEC 62443 clause, because we
    don't hold the standard).
  - `none`: a whole-document citation.
- `support` says how the source relates to the statement:
  - `paraphrase`: our wording of the source's point.
  - `related`: the source supports the statement but doesn't state it.
- Plus statement wording is nice-plus's own. Where the role-level rationale says
  *Inferred*, that is our judgment.
- **Copyrighted standards** (ISA/IEC 62443, IEC 62264, IEC 61131-3): cite by part, and by
  clause once verified. Paraphrase only. Their text never goes in this repo.

## Sources

| Source | Version | Use | Licence |
|---|---|---|---|
| [NICE Framework Components](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions) | 2.2.0, 2026-04-28 ([change log](https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/current-version/change-logs)) | roles, TKS statements | US Gov work |
| [MITRE ATT&CK for ICS](https://attack.mitre.org/matrices/ics/) | 20.1 | technique links | ATT&CK terms of use |
| [NIST SP 800-82r3](https://csrc.nist.gov/pubs/sp/800/82/r3/final) | Rev. 3, 2023-09 | citations (section + PDF page) | US Gov work |
| [NISTIR 8183r1](https://csrc.nist.gov/pubs/ir/8183/r1/final) | Rev. 1, 2020-10 | manufacturing context | US Gov work |
| [DOE National CIE Strategy](https://www.energy.gov/ceser/articles/us-department-energys-doe-national-cyber-informed-engineering-cie-strategy-document) | June 2022 | CIE principles | US Gov work |
| [INL CIE Implementation Guide](https://www.osti.gov/biblio/1995796) | v1.0 (INL/RPT-23-74072), 2023-08-07 | CIE principles by lifecycle phase | US Gov-sponsored report |
| [Secure PLC Coding Practices: Top 20 List](https://www.plc-security.com/) | v1.0, 2021-06-15 | controller programming | cite and paraphrase |
| ISA/IEC 62443-2-1, -2-4, -3-2, -3-3; IEC 62264-1; IEC 61131-3 | not held | part-level citations | copyrighted |
| Cyber Fire `operationaltechnology` puzzles | git commit in data | example coverage | puzzles not public; only paths, NICE tags, objective lines and INL release IDs are published here |

The Current Versions page showed "April 28, 2025" for v2.2.0 on 2026-11-20, but the
change log says 28 April 2026. v2.1.0 came out in December 2025, so we record 2026-04-28
(see `sources/nice/v2.2.0/provenance.json`).

### Observations on the NICE v2.2.0 data
- NICE already has an OT role, **DD-WRL-009 Operational Technology (OT) Cybersecurity
  Engineering**, with 108 statements (38 tasks, 44 knowledge, 26 skills). NICE Plus
  extends it rather than duplicating it.
- 7 of 11 competency areas, including **NF-COM-010 Operational Technology (OT)
  Security**, have no statements linked to them in the JSON.
- 348 statements are linked to no work role (`framework.json` →
  `observations`). Four of these are tagged by Cyber Fire puzzles: K1012, S0542, S0757
  and S0794.

## Roles

Each role has a status:
- `stub`: title, description, related NICE roles and open questions; no statements yet.
- `draft`: statements linked and cited, not yet reviewed by outside practitioners.
- `reviewed`: none yet.

A role either **extends** a NICE role (inherits all of its statements and flags each one
core or additional) or is **new**, drawing on `related` NICE roles. Each role lists its
`open_questions`, which are the best place for reviewers to start.

| ID | Role | Status | Extends | Related | Statements | Inherited / added NICE / plus |
|---|---|---|---|---|---|---|
| PR-OT-001 | OT Cybersecurity Engineer (Manufacturing) | draft | DD-WRL-009 |  | 166 (130 core) | 108 / 25 / 33 |
| PR-OT-002 | Controls / Automation Engineer (Security Duties) | draft |  | DD-WRL-009 | 47 (35 core) | 0 / 23 / 24 |
| PR-OT-003 | OT Cyber Defense Analyst | draft | PD-WRL-001 | DD-WRL-009 | 224 (76 core) | 205 / 10 / 9 |
| PR-OT-004 | ICS Incident Responder | draft | PD-WRL-003 | PD-WRL-002, DD-WRL-009 | 125 (56 core) | 106 / 9 / 10 |
| PR-OT-005 | Control Room Operator (Cyber-Aware) | draft |  | DD-WRL-009 | 13 (11 core) | 0 / 7 / 6 |
| PR-OT-006 | OT Security Architect | draft | DD-WRL-001 | DD-WRL-009 | 250 (79 core) | 218 / 14 / 18 |
| PR-OT-007 | Chief Operational Technology Officer | draft | OG-WRL-007 | DD-WRL-009, OG-WRL-014 | 117 (46 core) | 99 / 6 / 12 |
| PR-OT-008 | Functional Safety and Cybersecurity Engineer | stub | | DD-WRL-009 | | |
| PR-OT-009 | System Integrator Security Engineer | stub | | DD-WRL-007, DD-WRL-009 | | |
| PR-OT-010 | OT Product Security Engineer | stub | | DD-WRL-003, DD-WRL-004, DD-WRL-005 | | |
| PR-OT-011 | OT Network Engineer | stub | | IO-WRL-004 | | |
| PR-OT-012 | OT Systems Administrator | stub | | IO-WRL-005 | | |
| PR-OT-013 | Industrial Cybersecurity Technician | stub | | DD-WRL-009 | | |
| PR-OT-014 | ICS Forensic Analyst | stub | | PD-WRL-002 | | |
| PR-OT-015 | ICS Threat Analyst | stub | | PD-WRL-006 | | |
| PR-OT-016 | OT Vulnerability Assessor | stub | | PD-WRL-007 | | |
| PR-OT-017 | OT Cybersecurity Program Manager | stub | | OG-WRL-014 | | |
| PR-OT-018 | OT Risk and Consequence Analyst | stub | | DD-WRL-009 | | |
| PR-OT-019 | OT Security Assessor | stub | | OG-WRL-012 | | |
| PR-OT-020 | OT Supply Chain Risk Analyst | stub | | OG-WRL-017 | | |
| PR-OT-021 | OT Cybersecurity Instructor and Exercise Designer | stub | | OG-WRL-005, OG-WRL-004 | | |

Notes on the figures:
- Roles that extend a large IT-oriented NICE role (e.g. PD-WRL-001, DD-WRL-001) inherit
  every statement but flag most of them `additional`. The `core` list is the OT-relevant
  subset, chosen by nice-plus.
- The Controls / Automation Engineer and the Control Room Operator have no NICE parent.
  NICE has no role for the people who program controllers or operate the process.
- DD-WRL-009's description names "industrial cybersecurity technicians", but NICE never
  defines that role; PR-OT-013 is a stub for it.

### PR-OT-001 OT Cybersecurity Engineer (Manufacturing)

PR-OT-001 is the one deliberate sector specialization: a manufacturing version of
**DD-WRL-009**. It covers PLC-based production lines and machine cells, the operations
systems around them, and the machine builders and integrators who connect to them.

| | Count | Notes |
|---|---|---|
| Inherited from DD-WRL-009 | 108 | 86 core, 22 additional (general compliance, privacy, communication, admin) |
| Added NICE statements from other roles | 25 | 17 core, 8 additional. Chosen by sweeping all NICE statements for relevance, e.g. S0920 segmentation by criticality, K0915 network architecture, T1020 operational and safety impact, T1454 secure IT/physical/embedded interfaces, T1920 configuration baselines, K1002 SCADA |
| New plus statements | 33 | 21 from the first draft, plus 12 Cyber-Informed Engineering statements; all DRAFT and cited |
| **Total** | **166** | 130 core, 36 additional |

Its plus statements fill these gaps:
- ISA-95/MES layering
- manufacturing protocol families
- controller programs and project files as assets
- controller operating modes and key switches
- vendor, machine-builder and integrator access
- production consequences
- Cyber-Informed Engineering
- ATT&CK for ICS
- backups and integrity checks for controller logic
- detecting unauthorized logic and setpoint changes
- remote-access requirements
- transient assets and removable media
- scheduling changes around production
- engineering workstation security
- passive monitoring
- integrator contracts
- reading controller logic
- configuring controller security features
- protocol traffic analysis
- testing without disrupting production

See `plus/statements.json` and `plus/roles/*.json`.

## Cyber-Informed Engineering (PC-OT-001)

Cyber-Informed Engineering (CIE) uses engineering design, not only added security controls,
to eliminate or limit the consequences a cyber attack on an industrial system could cause,
across the whole lifecycle. It is aimed at the engineers and technicians who design, build,
operate and maintain physical systems, not only at security specialists. So NICE Plus
models it as a **competency area** any role can draw on, following the NICE Framework's own
competency areas.

The area is organized by the 12 principles in DOE's National CIE Strategy (2022, pp. 12-14)
and INL's CIE Implementation Guide (v1.0, 2023). Statements can be new plus statements or
existing NICE ones:

| Principle | Statements |
|---|---|
| 1. Consequence-focused design | PT-OT-0027, PS-OT-0009, PK-OT-0006, T2042, T2035 |
| 2. Engineered controls | PT-OT-0028, PK-OT-0017, T2041 |
| 3. Secure information architecture | PT-OT-0029, PT-OT-0017, PT-OT-0018 |
| 4. Design simplification | PT-OT-0030, PT-OT-0026 |
| 5. Resilient layered defenses | PT-OT-0031, K0791 |
| 6. Active defense | PT-OT-0032, K1290, K1291 |
| 7. Interdependency evaluation | PT-OT-0033, T1020 |
| 8. Digital asset awareness | T2047, T2028, K1307 |
| 9. Cyber-secure supply chain controls | PT-OT-0009, PT-OT-0023, T1399 |
| 10. Planned resilience with no assumed security | PT-OT-0034, PT-OT-0001, PT-OT-0014 |
| 11. Engineering information control | PT-OT-0035 |
| 12. Cybersecurity culture | PT-OT-0020, PT-OT-0024 |

Two statements apply to the whole area: PK-OT-0007 (CIE principles and consequence-driven
methods) and PK-OT-0018 (the systems engineering lifecycle).

Where the statements are used:
- **Core in:** the OT Cybersecurity Engineer (PR-OT-001), the Controls / Automation
  Engineer (PR-OT-002) and the OT Security Architect (PR-OT-006).
- **Additional in:** the Chief OT Officer (PR-OT-007).

Each export lists a statement's competency areas in `competency_areas`, and
`export/competency_areas.json` describes the area.

Engineering information control has only one statement, and CIE comes from the energy
sector, so this area especially needs review.

## Coverage

Coverage records which existing training modules address which statements.
- Each collection is one file in `data/coverage/`.
- `provenance` is `author-tagged` when the module author assigned the tag, and
  `inferred` when nice-plus proposed the mapping (`plus/coverage_map.json`, optional).
  Neither has been independently verified.
- **Cyber Fire puzzles are one example collection, not the main use case.** Only paths,
  KSA tags, objectives and INL release IDs are imported. Puzzle text and answers are
  never read into this repo. Many `objective` values are lab labels ("Complete Lab 2"),
  not learning objectives.
- Puzzle tags only use NICE IDs, so plus statements start at zero coverage until a
  collection tags them or an inferred mapping is added.
- Every export reports coverage by basis (`coverage.summary.by_basis`), so coverage of
  inherited statements is never hidden inside a total.
- PR-OT-001: 12 of 166 statements are covered, all NICE knowledge or skill statements and
  no tasks. By basis: inherited 3/108, added NICE 9/25, plus 0/33.
- Uncovered statements (`coverage.gaps`) are candidates for new training modules.

## Export contract (nice-plus → ottobotto)

`export/roles/<role id>.json` contains one role. The full schema is
`schema/role-export.schema.json`, and `export/index.json` lists the roles.

```jsonc
{
  "schema_version": "0.3.0",          // consumers must check; see versioning below
  "kind": "nice-plus.role",
  "notice": "DRAFT. … not a NIST product …",   // show wherever the role is presented
  "role": {
    "id": "PR-OT-001", "title": "…", "status": "draft",   // stub | draft | reviewed
    "source": "plus", "category": "DD",
    "description": "…",
    "extends":  [{"role": "DD-WRL-009", "title": "…"}],   // NICE roles whose statements are inherited
    "related":  [],                                       // NICE roles drawn on without inheriting
    "overlaps": [{"role": "DD-WRL-001", "title": "…", "shared": 32, "of_nice_role": 218, "jaccard": 0.094}],
    "citations": [ … ],
    "open_questions": ["…"]
  },
  "frameworks": {"nice": {"version": "2.2.0", "released": "2026-04-28", …}, "attack_ics": {"version": "20.1", …}},
  "statements": [{
    "id": "PT-OT-0002", "type": "task", "text": "…", "source": "plus", "nice_version": null, "status": "draft",
    "link": {"flag": "core", "basis": "plus", "via": null, "rationale": null},
    "relates_to_nice": [{"id": "T1243", "relation": "refines"}],
    "ot_context": {"purdue_levels": ["1","2"], "sectors": ["manufacturing"], "protocol_families": []},
    "attack_ics": [{"id": "T0889", "name": "Modify Program"}],
    "citations": [{"source": "nist-sp-800-82r3", "locator": "…", "locator_status": "verified", "support": "related", "note": "…"}],
    "coverage": [],                   // or [{"module": "<collection>:<path>", "provenance": "author-tagged"|"inferred"}]
    "open_questions": [],
    "competency_areas": ["PC-OT-001"] // NICE NF-COM-### and plus PC-OT-### areas
  }],
  "coverage": {
    "collections": [{"id": "…", "title": "…", "role": "example coverage source", "commit": "…", "commit_date": "…"}],
    "summary": {"all": {"total": 154, "covered": 12}, "by_type": {…}, "by_flag": {…}, "by_source": {…}, "by_basis": {…}},
    "modules": [{"id": "…", "collection": "…", "path": "…", "objective": "…", "release_id": "…", "statements_in_role": ["K1002"]}],
    "gaps": ["T0067", …],
    "provenance_note": "…"
  },
  "sources": [ …registry entries cited in this file… ]
}
```

### Consumer rules
1. Read `schema_version`.
   - Same major version, newer minor: only optional fields were added, so ignore
     unknown fields.
   - Different major version (or `0.x` → `0.y` while pre-1.0): stop and update the
     consumer.
2. Show `notice` and each statement's `status`. Never present a `draft` statement as NIST
   content.
3. `statements` is ordered NICE first, then plus. Within each, tasks, then knowledge,
   then skills, then by ID.
4. `coverage.gaps` lists the statements no module covers yet. Each gap is a candidate for
   a new ottobotto module.
5. Treat `link.flag` as the priority: `core` before `additional`.
6. A `stub` role has an empty `statements` list. Show it in a catalogue, but don't plan
   training from it.

`export/competency_areas.json` describes the plus competency areas, with each group's
statements and citations.

Version history (see CHANGELOG.md):
- 0.2.0 added `role.related`, `role.open_questions`, `statements[].open_questions` and the
  `stub`/`reviewed` statuses.
- 0.3.0 added `statements[].competency_areas` and `export/competency_areas.json`.

## Next steps
- [ ] Practitioner review of the seven draft roles, especially the core/additional flags.
- [ ] Flesh out the stub roles.
- [ ] Coverage page and browse pages: self-contained HTML, no CDNs, light/dark, works
  offline.
- [ ] Verify the `to-verify` locators (ISA/IEC 62443 clauses need a copy of the standard).
- [ ] Optional inferred coverage mappings to plus statements (`plus/coverage_map.json`).
- [ ] Other sectors: tag sector-specific statements, e.g. energy and water.
- [ ] Review the Cyber-Informed Engineering competency area against the CIE guide's
  lifecycle questions, and fill the thin principles.

## Contributing and licence

Corrections and additions are welcome, from people and from their agents.
- People: see [CONTRIBUTING.md](CONTRIBUTING.md).
- Agents: see [AGENTS.md](AGENTS.md).
- Ready-made tasks: see [Help wanted](#help-wanted-tasks-for-people-and-their-agents).
- nice-plus code and content: MIT.
- NIST NICE content: a US Government work.
- ATT&CK for ICS: MITRE's terms of use.

See [LICENSE](LICENSE).
