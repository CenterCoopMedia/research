# Agent instructions

This file is the canonical project instruction file. Read it before work. `CLAUDE.md` is a pointer to this file.

## Scope and sources

This is the public research and reports hub for the Center for Cooperative Media. Use the supplied report, approved sources, and the established report template. Do not invent findings, citations, author details, licenses, data, or publication approval. Keep report content separate from repository setup.

Never commit credentials, private working data or source documents, private personal information, local agent state, or PR evidence images. Other unpublished research and working files stay outside unless Joe Amditis or a designated CCM project maintainer authorizes those specific materials for public work with the right to share them. Existing task instructions can provide that authority; do not ask again for work already authorized. Record the public scope in the report brief and revise approved public drafts on branches before report publication. Keep raw private source exports outside the repository. Ignore rules are a convenience, not a security boundary. Inspect the full proposed change before publication.

## Coordination

Read the pinned ledger and its recent comments before work. Respect holds. Add a signed active-work line for sustained work and remove it at handoff. Sign ledger comments with `From: <name> (<unique id>), <runtime>, <workspace>`. Keep issues, milestones, and the project current. Close deployment work after live verification.

## Implementation and review

Use plain HTML, CSS, JavaScript, and standard-library tools when they meet the report's needs. Keep dependencies small. Preserve approved design, accessibility, attribution, and source links. Use sentence case and clear language.

Inherit the model and effort selected by the active session. Do not add provider credentials, model pins, trust overrides, or approval bypasses to project settings. Keep local runtime policy in force. Use independent review from another model provider for agent-authored code and verify its findings.

This repository is public. Verify the Git origin and current GitHub visibility. Run tests, builds, lint, scanners, and other CI checks only on GitHub-hosted runners; never on fleet workers or local machines. Read source locally as needed. Do not bypass a failed check, suppress a secret finding, or weaken a guard to publish.

The initial repository foundation can use the reviewed first-push exception while no default branch exists. Later work uses pull requests. Before merge, verify the exact head, independent review, hosted checks, open review threads, holds, and session merge authority. Do not request a manual cloud-connector review unless the user asks.

## Publication

Read `docs/publishing.md`. Publish only approved files under `site/`. The hub belongs at `site/index.html` and reports at `site/reports/<slug>/index.html`. Do not publish placeholder reports. Use stable slugs and links that work under the `/research/` project path. Keep source records and rights statements with each report. A merged change is not proof of a successful live deployment.

Navigate browsers through structured element references or semantic locators. Screenshots verify results; do not use them to guess click coordinates.
