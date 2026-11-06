# Publishing reports

## Publication boundary

The Pages workflow uploads only `site/`. It does not upload the repository root, source documents, local work folders, or agent settings. The publication target is <https://centercoopmedia.github.io/research/>.

The repository foundation publishes a working research landing page. It publishes no report draft or template example. The checks require `site/index.html`; removing it fails the run and does not remove an existing Pages deployment. Reports arrive in separate reviewed content pull requests.

## File layout

Keep the hub at `site/index.html`. Put each report at `site/reports/<slug>/index.html`, with its approved assets in that report directory. Use `site/assets/` for shared public assets. Use a stable lowercase slug with hyphens.

Use relative links, or include the `/research/` prefix for site-root paths. A path such as `/assets/chart.js` points outside this project site. Keep report links stable after publication; use a redirect page if a move is necessary.

Only publish approved data needed by the report. Do not commit private inputs, source document exports, interview records, email addresses, credentials, or unpublished working files. Removing a link does not make a file private.

## Report requirements

Use the established CCM report template and the authoritative report text. Record the title, authors, publication date, source links, methodology, limitations, and rights statement. Use an explicit license only when the rights owner has approved it. The repository's code license does not license report content or data.

Provide semantic headings, keyboard access, visible focus, useful chart descriptions, readable contrast, and layouts that work on phones and wide displays. Interactive controls must have labels. Provide a text or table alternative for facts shown only in a chart. Use reduced-motion preferences when motion is present.

## Release process

1. Open or update the report proposal and publication checklist issues. Confirm editorial approval, sources, rights, and the intended URL.
2. Prepare the hub entry, report page, and approved assets on a branch. Review the complete public diff for private data and credentials.
3. Open a pull request. Use GitHub-hosted checks and an independent review for agent-authored code. Verify actionable review threads and current ledger holds before an authorized merge.
4. After merge, the workflow scans Git history, checks configuration, and requires `site/index.html`. It packages `site/` and deploys through the `github-pages` environment. Deployment has only the Pages and identity-token write permissions it needs.
5. Verify the actual public hub and report URLs. Check links, charts, keyboard controls, phone layout, and wide-screen layout through a structured browser snapshot. Record the commit, workflow run, URL, and verification time in the publication issue and ledger. Then close the issue.

No local or fleet CI runs are used for this public repository. Do not bypass a secret finding or failed publication check.

## Rollback

Create a pull request that reverts the faulty publication. Preserve the report's URL when possible. Merge with the same review and check requirements, then verify the new deployment. Keep the incident issue open until the public result is checked.

Keep a valid landing page in the replacement artifact. Deleting `site/index.html` from Git does not unpublish the existing site. For an urgent takedown, an authorized repository administrator must unpublish Pages in repository settings or deploy a clean replacement, then verify that the affected public URLs no longer serve the removed content. Address any public repository copies or artifacts as part of the incident. Revoke an exposed credential at its owner first.
