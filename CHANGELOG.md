# Changelog

## Unreleased

### Added
- **Cyber-Informed Engineering competency area PC-OT-001.**
  - It maps the 12 CIE principles (DOE National CIE Strategy, 2022; INL CIE Implementation
    Guide v1.0, 2023) to NICE and plus statements.
  - 12 new CIE statements: PK-OT-0017, PK-OT-0018, PT-OT-0027 to PT-OT-0035, PS-OT-0009.
  - These are linked into PR-OT-001, PR-OT-002, PR-OT-006 and PR-OT-007.
- **Plus competency areas** (`plus/competency_areas.json`, IDs `PC-OT-###`), with
  `export/competency_areas.json`.
- **Agent contribution support:**
  - `AGENTS.md`
  - ready-to-paste task prompts in the README
  - AI-assistance disclosure and duplicate checks on every issue template
  - a *Suggest a source* template and a pull request template
- **OT role catalogue: 21 roles.**
  - Seven drafts with linked statements:
    - PR-OT-001 OT Cybersecurity Engineer (Manufacturing)
    - PR-OT-002 Controls / Automation Engineer (Security Duties)
    - PR-OT-003 OT Cyber Defense Analyst
    - PR-OT-004 ICS Incident Responder
    - PR-OT-005 Control Room Operator (Cyber-Aware)
    - PR-OT-006 OT Security Architect
    - PR-OT-007 Chief Operational Technology Officer
  - Fourteen stubs (PR-OT-008 to PR-OT-021) with descriptions, related NICE roles and open
    questions.
- **29 new plus statements**, for 50 in total, all cited.
- **New source:** *Secure PLC Coding Practices: Top 20 List* v1.0 (cited by practice
  number).
- **Role statuses** `stub | draft | reviewed`, plus a status on plus statements.
- **New role fields:** `related` (NICE roles drawn on without inheriting) and
  `open_questions`. Statements can also carry `open_questions`.
- **Inheritance:** `inherit` takes `core` or `additional` exception lists, so a role can
  inherit a large NICE role with most statements flagged additional.
- **Repo files:** `LICENSE` (MIT, with notices for NIST and MITRE material), `CONTRIBUTING.md`, and
  issue templates.

### Changed
- **Export `schema_version` is now 0.3.0:**
  - 0.2.0 added `role.related`, `role.open_questions`, `statements[].open_questions`, and
    the `stub`/`reviewed` statuses.
  - 0.3.0 added `statements[].competency_areas`.
- **Plus statements that apply to any OT sector** now have `ot_context.sectors: []`.
- **Cyber Fire coverage data** records the repository name instead of its remote URL.

## 0.1.0 (2026-11-20)

### Added
- Data model and export contract (`schema_version` 0.1.0).
- Pristine NICE Framework Components v2.2.0 and ATT&CK for ICS v20.1, with importers.
- Cyber Fire puzzle tag import as an example coverage source.
- Draft PR-OT-001 OT Cybersecurity Engineer (Manufacturing).
