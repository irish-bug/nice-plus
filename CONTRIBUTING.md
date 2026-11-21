# Contributing to NICE Plus

NICE Plus is a first attempt at extending the NIST NICE Framework for OT/ICS
cybersecurity roles. It will have gaps and mistakes. Corrections from people who do this
work, and from the AI agents they use, are the point of publishing it.

**Using an AI agent?** Great, and please do.
- Point it at [AGENTS.md](AGENTS.md), which has the rules that keep agent contributions
  trustworthy.
- Give it a ready-made task from the README's *Help wanted* section.
- Read what it produces before you submit it, and tick the AI-assistance box on the issue
  or PR.

## Ways to help

- **Challenge something.** A statement is wrong, in the wrong role, flagged core when it
  should be additional, or cited badly. Open a *Challenge a statement or role* issue.
- **Propose a statement.** Open a *Propose a statement* issue.
- **Suggest a source.** Know a public, citable source on OT/ICS work roles or tasks that
  we don't use? Open a *Suggest a source* issue.
- **Flesh out a stub role.** Roles with `status: stub` have a description and open
  questions but no statements yet. Open a *Propose or flesh out a role* issue, or send a
  pull request.
- **Answer an open question.** Every role lists `open_questions`; start there.
- **Verify a citation.** Search `plus/` for `"locator_status": "to-verify"`. If you can
  check one against the source (especially ISA/IEC 62443 clauses), tell us the clause and
  whether it supports the statement.

## Rules for content

1. **NICE text is never edited.** NICE statements and roles are quoted exactly as NIST
   publishes them. If NICE wording is the problem, propose a plus statement that refines it.
2. **Plus IDs are permanent:**
   - statements are `PT-OT-####`, `PK-OT-####`, `PS-OT-####`
   - roles are `PR-OT-###`
   - IDs are never renumbered or reused; a withdrawn item keeps its ID
3. **Every plus statement and role cites a source** listed in `sources/registry.json`:
   - `locator_status`: `verified` only if you read the source at that location;
     `to-verify` otherwise; `none` for a whole-document citation.
   - `support`: `paraphrase` only if the source actually says it; `related` if it supports
     the statement without saying it.
4. **No copyrighted standards text.** Cite ISA/IEC and similar standards by part and
   clause, and write statements in your own words.
5. **Statements belong to roles on merit.** Choose them for what the job needs, not
   because existing training covers them.
6. **General OT first.** Roles apply across sectors. Put sector-specific statements in
   `ot_context.sectors` (an empty list means any sector).
7. **ATT&CK for ICS IDs** go only in `attack_ics`, and must be active techniques in the
   ATT&CK version in `data/attack-ics/`.

## Pull requests

```sh
pip install -r requirements-dev.txt
make build   # validates everything and rebuilds export/
make check   # JSON Schema validation
```

- Edit `plus/` (and `sources/registry.json` for new sources). Never hand-edit `data/` or
  `export/`, which are generated; commit the regenerated files with your change.
- `build.py` must pass. It rejects:
  - ID clashes
  - unknown sources
  - revoked ATT&CK IDs
  - duplicate links
  - plus statements no role uses
- Keep each PR to one topic, and say in the description what sources you checked.
- Changes to `schema/role-export.schema.json` change the contract with downstream tools.
  Bump `EXPORT_SCHEMA_VERSION` in `scripts/common.py` and add a CHANGELOG entry.

## Licence

By contributing you agree that your contribution is licensed under the MIT License.

See `LICENSE`.
