# CCM report template

`ccm/` contains the unchanged files from the existing CCM template distribution. Use it for future report design and editing; do not publish its invented sample as research.

- Requested template: <https://jamditis.com/ccm-report-template/>
- Browser guide: <https://jamditis.com/ccm-report-template/guide.html>
- Design guide: [ccm/DESIGN.md](ccm/DESIGN.md)
- Editing and build guide: [ccm/README.md](ccm/README.md)
- Source: `jamditis/stash`, commit `46f9fbb929d83143239e9c4976801ec4bb2783f3`, `docs/ccm-report-template/template.zip`.
- File hashes and archive hash: [ccm-source.json](ccm-source.json).

Only that authorized distribution was copied. No stash history or unrelated files were transferred. The template's README states that all sample people, numbers, quotations, and results are invented. The sample HTML and JSON remain outside `site/`, so the Pages artifact does not publish them.

The `fonts/` directory includes each bundled font's SIL Open Font License notice. Preserve those notices when copying fonts into a report. Do not assume that a report's content or third-party assets use the repository code license.

## Use and update

Read the design guide and editing guide before changes. Use a separate report work folder and replace every sample fact with verified source material. Keep private source exports outside the repository. Run builds and checks on GitHub-hosted runners under the project contract; the template needs Python 3.11 or later and the standard library.

For an update, select an authorized upstream commit, obtain its template distribution, and review the exact change. Update the provenance and file hashes together. Do not copy unrelated private files or suppress scanner findings. Recheck report output before publication.
