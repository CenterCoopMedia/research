# Boom or bust: Research handoff

This folder is the editing brief for ChatGPT dot and local editors. It contains no report draft, private source export, or published report page.

Joe Amditis authorized this public editing brief's title, byline, source-document link, template reference, and location-count question. The current setup scope covers only those items. The draft body, quotations, findings, and data beyond that question are outside this scope and must not be copied into public report JSON, branches, or issues as part of setup. Future task instructions can authorize specific materials for public design iteration under the repository rules. Raw private source exports stay outside the repository, and report publication remains separate. The source document's owner controls access to that document.

## Source and template

- Source title: *Boom or bust: The state of ethnic and community media in New Jersey, 2026*.
- Source byline: Anthony Advincula (Oni).
- Authoritative working draft: [Google document](https://docs.google.com/document/d/1lm0ocUZVljDeaMQNELik8324zfIhJncl0b2Bin4FKc0/edit). Keep this document read-only unless its owner authorizes a change.
- Requested template: <https://jamditis.com/ccm-report-template/>.
- Local template: [templates/ccm](../../templates/ccm/), including `DESIGN.md` and the editing guide.

The current draft remains in the source Google document. No report JSON or report page has been created here. ChatGPT dot will handle report design iteration using this repository.

## Editorial question

Location counts need author clarification. The source's data highlights gives 90 New Jersey-based outlets and 38 out-of-state outlets. Its findings gives 95 and 33. Both total 128. The findings also labels 95 of 128 as 72.4%; that ratio is about 74.2%. Do not choose or correct these figures without confirmation. Community subtotals also need context before they are treated as an exhaustive partition.

Status: Waiting for author clarification. The authorized clarification email was sent on November 6, 2026. The coordinator owns response follow-up. Do not treat a sent question as a verified correction.

## Editing workflow

Read the repository's [AGENTS.md](../../AGENTS.md), then the template's design and editing guides. Use this folder as the report brief. Keep proposed source changes separate from the authoritative document. Record answers and source approvals in [issue 3](https://github.com/CenterCoopMedia/research/issues/3).

Shared agent settings are `.codex/config.toml` and `.claude/settings.json`. Codex uses TOML, as [its settings note](../../.codex/README.md) explains. Select this repository in the ChatGPT GitHub connection before asking dot to read or edit it; app permissions are separate from repository access.

Use a branch and pull request for report work. Keep any future report output outside `site/` until its content and publication are approved. Build and check through GitHub-hosted workflows, with no local or fleet CI.

## Before publication

- Resolve the location counts and percentage with the author.
- Verify all facts, quotations, source links, author details, and data relationships.
- Record editorial approval and report-specific rights.
- Replace all template examples and sample metadata.
- Check accessibility, keyboard controls, phone layout, wide-screen layout, and links.
- Complete independent review and hosted checks for the publication head.
- Use a separate publication checklist and verify the actual deployed URL before closing it.
