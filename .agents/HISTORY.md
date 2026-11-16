# AGENTS.md — HISTORY

Recorded decisions with git references. Read when relevant to current task.
Acts as simple long-term memory for the project.

## Format

| Date       | Decision   | Rationale   | Git ref          |
| ---------- | ---------- | ----------- | ---------------- |
| YYYY-MM-DD | [describe] | [why]       | [commit hash/tag] |

## Guidance

- Record decisions that would be costly to rediscover.
- Note false turns and why they were rejected.
- Link to relevant commits.
- Keep entries brief — enough to reconstruct reasoning.
- When this file grows too large, archive older entries to
  `.agents/history/` and leave a pointer here.

## Decisions

| Date | Decision | Rationale | Git ref |
| ---- | -------- | --------- | ------- |
| 2026-11-16 | Rename the project to `sdo-writer`: repository, PyPI name, console script and agent file | The agent and its skills must outlive the host they run in today, so no host prefix. `sdo-writer-opencode` keeps the lock-in, `sdo-writing` collides with a skill | `425ba33` |
| 2026-11-16 | Stop vendoring the skills; serve them from `sdo-skills-mcp` and write one `mcp.servers` entry instead | One source of truth for the rule text; a rules fix no longer needs an installer release, and a copied snapshot drifted from the skills repository by construction | this commit |
| 2026-11-16 | Never rewrite `opencode.jsonc`; print the entry instead | A rewrite would silently delete the user's comments, which is worse than a copy-paste | this commit |
| 2026-11-16 | Keep `skills` in the manifest as a cleanup list only | An install from before the MCP server copied skill directories into the configuration; only a recorded list lets `update` and `uninstall` remove exactly those | this commit |
