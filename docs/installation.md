---
title: Installation
---

## Installation

The package writes one agent file and one MCP server entry into an OpenCode configuration
directory. The skills themselves are not copied: the entry starts `sdo-skills-mcp`, which serves
them for the selected profile.

### One line

```bash
uvx --from "git+https://github.com/jr2804/sdo-writer" sdo-writer init --profile etsi
```

`uvx` downloads the package, runs the `init` command and throws the temporary environment away.
The agent file, the server entry and the manifest stay behind.

The package is not on PyPI yet, so `uvx` needs the repository as its source. Most people alias that
once:

```bash
alias sdo-writer='uvx --from "git+https://github.com/jr2804/sdo-writer" sdo-writer'
```

The examples below use that alias.

### Where things land

| Path | Content |
| ---- | ------- |
| `~/.config/opencode/agents/sdo-writer.md` | The writer agent |
| `~/.config/opencode/opencode.json` | One `mcp.servers.sdo-skills` entry that starts the skills server |
| `~/.config/opencode/sdo-writer.json` | The manifest: profile, agent file, server name, config file and timestamp |

On Windows the global directory is `%USERPROFILE%\.config\opencode`. When `XDG_CONFIG_HOME` is set,
it wins.

The first time OpenCode starts the server it runs `uvx --from
git+https://github.com/jr2804/sdo-skills-mcp sdo-skills-mcp serve --profile <id>`, so the machine
needs network access once per release. After that `uvx` reuses its cache.

### Choosing a target

```bash
# Global: available in every project (default)
sdo-writer init --profile etsi

# One project only
sdo-writer init --profile etsi --project /path/to/repo

# An explicit configuration directory
sdo-writer init --profile etsi --config /path/to/.opencode
```

### The skills root

The server reads the skills from a directory tree. Pass `--skills-root` once per root, either to
`init` or to `entry`:

```bash
sdo-writer init --profile etsi --skills-root ~/src/sdo-skills/skills
```

The flag is repeatable and ends up in the server command as `--root <path>`. Without it the server
falls back to its own default, the `SDO_SKILLS_ROOTS` environment variable, and finally to the skill
directories that ship inside the server package.

### Profiles

```bash
sdo-writer profiles
```

| Profile | Focus |
| ------- | ----- |
| `etsi` | Contributions, meeting documents, work items, ETSI deliverables, portal tooling |
| `3gpp` | TDoc conventions, change requests, working groups, specification metadata |
| `itut` | Contribution rules, recommendation structure, patent policy |

The profile decides which skills the server serves, not which files are copied. The `etsi` profile
also serves the two tool skills `etsi-portal-tool` and `etsi-meeting-report`.

### Checking the result

```bash
sdo-writer status
```

The output names the profile, the agent file and the server entry. A `!` line means something the
installer wrote is missing or the configuration is no longer plain JSON; `update` restores it.

### Updating

```bash
sdo-writer update --profile etsi
```

`update` is `init` without `--dry-run`: it rewrites the agent, replaces the server entry with the
one for the new profile and refreshes the manifest.

### Removing

```bash
sdo-writer uninstall
```

Only what the installer wrote is removed: the agent file, the `mcp.servers` entry and the manifest.
Skill directories that an earlier, vendoring install left behind are removed too, because the
manifest lists them.

### A configuration with comments

OpenCode reads both `opencode.json` and `opencode.jsonc`. A JSONC file carries comments, and a
rewrite would lose them, so the installer never touches it. It prints the entry and leaves the file
alone:

```text
~/.config/opencode/opencode.jsonc could not be rewritten, so add this by hand:
{
  "mcp": {
    "servers": {
      "sdo-skills": {
        "type": "local",
        "command": ["uvx", "--python", "3.14", "--from", "git+https://github.com/jr2804/sdo-skills-mcp", "sdo-skills-mcp", "serve", "--profile", "etsi"]
      }
    }
  }
}
```

`entry` prints only that JSON, which makes the copy-paste short:

```bash
sdo-writer entry --profile etsi
```

### Requirements

- Python 3.13 or newer to run the installer (through `uvx`, nothing has to be installed).
- `uvx` on the machine that runs OpenCode, because the server is started that way.
- [mise](https://mise.jdx.dev/) for the skills to pull their tools on demand. The skills call
  `mise x <tool> -- <command>`; without mise they report what is missing instead of failing
  silently.
