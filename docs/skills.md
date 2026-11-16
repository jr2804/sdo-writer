---
title: Skills
---

## Skills

The skill text does not live in this repository. It comes from
[jr2804/sdo-skills](https://github.com/jr2804/sdo-skills) and is served to the host by
[jr2804/sdo-skills-mcp](https://github.com/jr2804/sdo-skills-mcp). Nothing is copied into the
OpenCode configuration.

### Why the split

The three parts change on different schedules. The Directives are revised twice a year, a document
skeleton changes when a body changes its templates, the writing style changes when you decide it
does. The agent prompt changes when the workflow does, the server when the skill format or the MCP
extension does. Keeping the text in its own repository means a rules fix does not need a new agent
release, and the agent does not need to carry the rules.

The path is:

```text
sdo-skills        the skill text, one directory per skill
     │
     ▼
sdo-skills-mcp    one MCP server per profile, serving those directories
     │
     ▼
sdo-writer        the agent prompt and its permissions (this repository)
```

### The profiles

The server owns the layer table and the profile catalog. A profile identifier is the only thing this
package sends to it: the same `etsi` that renders the agent selects the skills.

| Profile | Layers | Skills |
| ------- | ------ | ------ |
| `etsi` | `common`, `etsi`, `tools` | 11 |
| `3gpp` | `common`, `3gpp` | 13 |
| `itut` | `common`, `itut` | 7 |

| Layer | Holds |
| ----- | ----- |
| `common` | Writing style, DOCX mechanics, drafting skeletons, IPR notes, project setup |
| `etsi` | ETSI structure, the Directives, procedures and approval routes, portal and specification tooling |
| `3gpp` | 3GPP structure, meetings, working groups, releases, specification metadata, TDoc conventions, change requests, portal session handling |
| `itut` | ITU-T working methods, recommendation structure, contribution rules |
| `tools` | The portal CLI and the meeting report builder |

The counts above come from the server's own profiles; this repository does not repeat the layer
table, because two copies of it would drift.

### How the agent reaches a skill

Two paths, one content:

- Hosts that implement the MCP Skills extension list and read the skills natively. OpenCode does
  not do that today.
- Every host can call the server's two tools, `sdo_list_skills` and `sdo_read_skill`. The agent
  prompt tells the model to call them.

The agent file carries the permissions for both: one `allow` rule per server tool, and
`opencode_read_mcp_resource` on `sdo-skills:*` for the resource path. Local skills on disk stay
denied, so a copy that somebody drops into `~/.config/opencode/skills` cannot shadow the served
version.

### The shape of a skill

```text
<skill-id>/
├── SKILL.md          # the entry point: what it is, when to use it, the short rules
├── references/       # the long text, read only when it is needed
├── assets/           # skeletons, templates, images
├── scripts/          # helpers, each with PEP 723 metadata
└── examples/         # worked examples
```

`SKILL.md` stays small. The linter in the skills repository holds the body under 8 KiB; anything
longer moves into `references/`. A skill that answers one question fits in one prompt; a skill that
answers a family of questions gets a directory.

The frontmatter carries a `name` and a `description`. The description is a list of triggers, not a
summary: the agent matches the request against it to decide whether to load the skill.

### Adding a skill

1. Write it in the skills repository, under the layer that owns the topic, and let the linter there pass.
2. Add it to that layer in `sdo-skills-mcp`'s `catalog.toml`.
3. Run `sdo-skills-mcp check --profile etsi` to confirm that every skill of the profile resolves.
4. Nothing changes here. This repository carries no skill list, only the layers a profile serves.

### Rules for the skills

The skills repository enforces these through its linter:

- A `SKILL.md` body stays under 8 KiB. Overflow moves to `references/`.
- The description is a trigger enumeration.
- Every referenced path - `references/`, `assets/`, `scripts/` - must exist.
- Every mentioned skill identifier must exist.
- External tools are invoked as `mise x <tool> -- <command>`, so that nothing has to be installed by hand.
