# Contributing

Start with an issue that states the intended result and the approved sources. Use the report proposal form for new research. Add the closest milestone and the matching labels. Keep embargoed research and private data outside public issues. Other unpublished research and working files stay outside unless Joe Amditis or a designated CCM project maintainer authorizes those specific materials for public work with the right to share them. Existing task instructions can provide that authority. Record the public scope in the report brief and revise approved public drafts on branches before report publication.

Make a focused branch and pull request. Explain the change, its sources, and how it was checked. Keep design and editorial decisions explicit. Give credit to report authors and source owners without adding agent attribution to commits.

Run repository checks through GitHub Actions. This public repository does not run CI on local or fleet machines. Agent-authored code also needs independent review from another provider. Do not commit screenshots used only as PR evidence.

For a publication, follow [the publication guide](docs/publishing.md) and open a publication checklist issue. Confirm source accuracy, rights, accessibility, responsive layout, and stable links. Merge requires a reviewed exact head, passing hosted checks, resolved actionable review threads, no conflicting hold, and merge authority.

After a deployment, check the actual public URL and record the deployed commit and workflow run. Close the publication issue only after that check. Remove stale claims and branches when work ends.
