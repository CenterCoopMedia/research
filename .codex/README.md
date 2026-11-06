# Codex settings

Codex reads shared project settings from `.codex/config.toml`. It does not use a project `settings.json` file. See the [official configuration guide](https://developers.openai.com/codex/config-basic/).

The shared file uses workspace writes and approval on request. It leaves the selected model and reasoning effort to the active session. Command-line options and managed policy can take precedence. Trust remains a user or runtime decision; this repository does not grant itself trust.

Keep credentials, personal overrides, logs, and session state outside this public repository. Read `AGENTS.md` for the project contract.
