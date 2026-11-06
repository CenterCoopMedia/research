# Security

Do not post credentials, private research data, or an exploitable vulnerability in a public issue.

Use [private vulnerability reporting](https://github.com/CenterCoopMedia/research/security/advisories/new) for a sensitive security report. Include the affected URL or file, the impact, and steps to reproduce. Do not include a working credential value.

If a secret is exposed, revoke or rotate it at its owner first. Removing a file or changing Git history does not revoke a credential. Notify the repository maintainer through the private report and record the repair without repeating the value.

GitHub secret scanning and push protection are enabled. Hosted CI also scans Git history with Gitleaks using its upstream default rules. Do not add a baseline, rule suppression, or allowlist to hide a finding.

Only `site/` is eligible for Pages publication. Keep private input files outside the public repository, including outside ignored directories.
