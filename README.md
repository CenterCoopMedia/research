# Research and reports

Research and interactive reports from the [Center for Cooperative Media](https://centerforcooperativemedia.org/).

This repository holds the public site, approved report assets, and the work needed to publish and maintain them. Embargoed research, private working data, and credentials belong outside this public repository. Other unpublished research and working files stay outside unless Joe Amditis or a designated CCM project maintainer authorizes those specific materials for public work with the right to share them. Existing task instructions can provide that authority. Record the public scope in the report brief and revise approved public drafts on branches before report publication.

## Publication

The research hub is at <https://centercoopmedia.github.io/research/>. Its landing page links the repository, work board, and report template. Report publication follows a separate content review and release.

- `site/index.html`: The research hub.
- `site/reports/<slug>/index.html`: A report with a stable address.
- `site/assets/`: Shared public assets, when needed.
- `docs/publishing.md`: Publication requirements and the release process.

GitHub Actions scans the Git history for secrets and checks repository configuration. A successful run on `main` can publish only the `site/` directory. CI runs on GitHub-hosted runners.

## Work with ChatGPT dot or a local editor

Use this repository as the shared workspace. In ChatGPT, connect GitHub and make sure `CenterCoopMedia/research` is selected in the GitHub app's repository access. A new public repository is not always selected automatically. If it is missing from your chat, review the app's selected repositories, refresh the connection, and confirm that the chat can read this README. Repository access and an app's ability to edit or open pull requests are separate permissions.

In a local editor, clone `https://github.com/CenterCoopMedia/research.git` and work on a branch. Give the chat or coding agent the report work-folder path and ask it to read `AGENTS.md` first. Keep the source document unchanged and put proposed report changes through a pull request.

The first handoff is [Boom or bust, 2026](reports/boom-or-bust-2026/README.md). It records source links and an open data question. ChatGPT dot will handle report design iteration; this setup does not publish that report.

The [CCM report template](templates/README.md) is available locally under `templates/ccm/`, with its design guide and source provenance. Its sample names, numbers, and quotes are invented. Template examples stay outside `site/`.

## Work tracking

Use the [research project](https://github.com/orgs/CenterCoopMedia/projects/6) for planned and active work. The [pinned ledger](https://github.com/CenterCoopMedia/research/issues/1) records active agents, holds, and release receipts. The first milestone is [Research hub launch](https://github.com/CenterCoopMedia/research/milestone/1).

Use an issue to propose a report, report a defect, or record publication checks. An issue that needs a deployment stays open until the published result is verified.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before a change. Agents must also read [AGENTS.md](AGENTS.md). Shared settings are in `.codex/config.toml` and `.claude/settings.json`; they do not select a model or store credentials.

## Rights

Repository code uses the [MIT license](LICENSE). Reports, data, images, quotations, and other third-party material retain their respective rights. Each report must state its own rights and any reuse terms. The code license does not grant rights to report content or data.
