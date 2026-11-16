# TOOLS — development-time tooling inventory

OpenCode coding agent project. Tooling surface:

| Tool | When to use |
| ---- | ----------- |
| `mise` | Every skill invokes tools through it: `mise x <tool> -- <command>`. Install once. |
| `uv` / `uvx` | Run installer and tests; publish; start `sdo-skills-mcp` from git. |
| `pytest` | Test suite, 100% coverage gate. |
| `ruff` + `pyreorder` | Lint/format; `mise run format`. |
| `ty` | Type checking (lint). |
| `rumdl` | Markdown lint: `mise run format-md`. |
| `zensical` | Docs site build. |
| `git` | History. |

MCP servers: none configured for this repo. OpenCode agent/skills run in user's environment.

Sibling deliverable: [`sdo-skills-mcp`](https://github.com/jr2804/sdo-skills-mcp) serves the same
skills over MCP. Its profile composition (`catalog.toml`, `profiles/*.toml`) mirrors
`src/sdo_writer/profiles/`; when the two disagree, the skills repository is right and both
copies are stale.
