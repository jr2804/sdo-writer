---
title: Profiles
---

## Profiles

A profile decides what the agent is called, how it is presented, which skills the server serves to
it, and which commands it may run.

Profiles are TOML files in `src/sdo_writer/profiles/`. They are part of the package, so they ship
with it.

### The three profiles

| Profile | Layers | Focus |
| ------- | ------ | ----- |
| `etsi` | `common`, `etsi`, `tools` | Contributions, meeting documents, work items, ETSI deliverables, portal tooling |
| `3gpp` | `common`, `3gpp` | TDoc conventions, change requests, working groups, specification metadata |
| `itut` | `common`, `itut` | Contribution rules, recommendation structure, patent policy |

The `common` layer is always included: it carries the writing style, the DOCX mechanics, the
drafting skeletons, the IPR notes and the project setup.

### Anatomy

```toml
id = "etsi"
title = "ETSI Writer"
description = "Drafts ETSI contributions, meeting documents, work item descriptions and deliverables (TS, ES, EN, TR, EG, GS, SR)."

[agent]
name = "sdo-writer"
mode = "primary"
color = "#2f6f9f"

[skills]
layers = ["common", "etsi", "tools"]

[tools]
allow = [
  "mise *",
  "uv run *",
  "uvx *",
  "npx *",
  "bunx *",
  "git status *",
  "git log *",
  "git diff *",
  "etsi-portal-tool *",
]

[notes]
body = """
## ETSI specifics

- **Two kinds of document.** ...
"""
```

#### `id`, `title`, `description`

The identifier is what `--profile` expects, and the same value is passed to the skills server. The
title and description are shown by the `profiles` command and written into the agent file.

#### `[agent]`

| Key | Meaning |
| --- | ------- |
| `name` | File name of the agent, without extension: `agents/sdo-writer.md` |
| `mode` | `primary` or `subagent` |
| `color` | Hex colour for the agent in the OpenCode interface |

There is no `temperature`: OpenCode V2 dropped the field, and the writer profiles never needed it —
the rules are the point, not the phrasing.

#### `[skills]`

The layers of the skills catalog that the server should serve. The layer table itself lives in
`sdo-skills-mcp`, not here: this repository names the layers, the server decides which skills they
contain.

#### `[tools]`

The commands the agent may run, written as the patterns OpenCode matches against. `mise *` covers the
on-demand tool calls; the `git *` entries are there for checking the state of a working document.

They are rendered into the agent's `permissions` list. The template opens with a broad
`shell *` rule set to `ask`, so anything that is not listed prompts before it runs.

#### `[notes]`

Body-specific guidance that is appended to the agent file. This is where the differences between the
bodies live: ETSI's contribution-versus-deliverable distinction, the approval routes, the portal.
A profile is a small fragment, not a fork of the agent.

### Writing a new profile

1. Copy the closest existing profile.
2. Give it an `id`, a `title` and a `description`.
3. List the layers you need.
4. Write the body-specific notes. If a rule matters for more than one body, it belongs in a common
   skill, not in a profile.
5. Add the profile to `sdo-skills-mcp`'s `profiles/` as well, because the server refuses a profile it
   does not know.

The profile is resolved in both places: this package renders the agent, the server resolves the
skills. If the two names drift apart, `sdo-writer init` succeeds but the server fails at startup with
an unknown profile.

### Agent file

The agent is rendered from the template in `src/sdo_writer/templates/`:

- `sdo-writer.md` - the V2 frontmatter, the `permissions` rules derived from `[tools]` and from the
  MCP server, and the body.
- `sdo-writer-body.md` - the shared behaviour, the same for every profile.

The rendered file lands in `agents/<name>.md` of the configuration directory, and OpenCode picks it
up from there. The skills are not part of the agent file: its permissions only grant access to the
server tools and the resources they serve.
