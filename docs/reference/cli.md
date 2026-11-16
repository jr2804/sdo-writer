---
title: CLI reference
---

## CLI reference

```text
sdo-writer [OPTIONS] COMMAND [ARGS]...
```

The package installs one command, `sdo-writer`. The examples below write it as
`sdo-writer ...`; without a local install that is
`uvx --from "git+https://github.com/jr2804/sdo-writer" sdo-writer ...`.

### `init`

Write the writer agent and the skills server entry for a profile.

```bash
sdo-writer init --profile etsi
```

| Option | Short | Default | Meaning |
| ------ | ----- | ------- | ------- |
| `--profile` | `-p` | none | Profile to install: `etsi`, `3gpp` or `itut` |
| `--config` | `-c` | the global config dir | OpenCode configuration directory to write to |
| `--project` | - | none | Install into the `.opencode` directory of this project |
| `--skills-root` | `-r` | none | Skills directory for the server; repeatable, passed through as `--root` |
| `--no-agent` | - | off | Write only the server entry and the manifest |
| `--dry-run` | - | off | Print the paths and the entry without writing anything |

The report names the profile, the configuration directory, the agent file and the server entry. When
the configuration is an `opencode.jsonc`, the file is left untouched and the entry is printed for you
to paste in.

### `update`

Re-install a profile: rewrite the agent and replace the server entry.

```bash
sdo-writer update --profile etsi
```

Takes the same options as `init`, without `--dry-run`.

### `status`

Show what is installed.

```bash
sdo-writer status
```

| Option | Short | Meaning |
| ------ | ----- | ------- |
| `--config` | `-c` | OpenCode configuration directory to inspect |
| `--project` | - | Inspect the `.opencode` directory of this project |

A `!` line names something that is missing or unreadable: the agent file, the server entry, or a
configuration that is no longer plain JSON.

### `entry`

Print the `mcp.servers` entry of a profile, and nothing else.

```bash
sdo-writer entry --profile etsi
```

| Option | Short | Meaning |
| ------ | ----- | ------- |
| `--profile` | `-p` | Profile whose entry should be printed |
| `--skills-root` | `-r` | Skills directory for the server; repeatable |

The output is the JSON a hand-written `opencode.jsonc` needs.

### `uninstall`

Remove the agent, the server entry and the manifest.

```bash
sdo-writer uninstall
```

Only what a previous install wrote is removed. Skill directories are removed when the manifest of an
earlier, vendoring install lists them; anything you created yourself stays.

### `profiles`

List the available profiles.

```bash
sdo-writer profiles
```

### Exit codes

| Code | Meaning |
| ---- | ------- |
| `0` | Success |
| `1` | No profile given, unknown profile, a broken profile, or a configuration section that cannot be merged |

### Examples

```bash
# See what an install would do
sdo-writer init --profile etsi --dry-run

# Install into one project
sdo-writer init --profile 3gpp --project .

# Point the server at a checkout of the skills repository
sdo-writer init --profile itut --skills-root ../sdo-skills/skills

# Print the entry for a hand-maintained opencode.jsonc
sdo-writer entry --profile etsi
```
