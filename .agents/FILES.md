# AGENTS.md — FILES

Single source of truth for paths, config keys, and naming conventions.
Kept compact — agents hallucinate less when they know where definitions live.

## Pattern

- One file owns each class of definition (paths, config defaults, enums).
- Import from that file. Never hard-code values in other modules.
- Variables that address files get `_file` suffix; directories get `_dir`.

## Project-specific sources of truth

| What                   | Where                                                           | Key names                                       |
| ---------------------- | --------------------------------------------------------------- | ----------------------------------------------- |
| Package source root    | `src/sdo_writer/`  | `__init__.py`, `__about__.py` (version)         |
| CLI entry points       | `src/sdo_writer/cli/`            | `app.py` (Typer app), `args.py`, `commands.py`  |
| Install logic          | `src/sdo_writer/installer.py`                          | `install`, `update`, `uninstall`, `status`      |
| MCP server entry       | `src/sdo_writer/mcp.py`                                | `MCP_SERVER_NAME`, `SERVER_PACKAGE`, `server_entry`, `with_server` |
| Filesystem locations   | `src/sdo_writer/paths.py`                              | `global_config_dir`, `config_file`, `agents_dir` |
| Profile model          | `src/sdo_writer/profile.py`                            | `Profile`, `load_profile`, `available_profiles` |
| Writer profiles        | `src/sdo_writer/profiles/*.toml`                       | `etsi.toml`, `3gpp.toml`, `itut.toml`           |
| Agent templates        | `src/sdo_writer/templates/`                            | `sdo-writer.md`, `sdo-writer-body.md`           |
| Installer manifest     | `<config-dir>/sdo-writer.json`                         | `Manifest`, `MANIFEST_VERSION`, `mcp_server`    |
| Skills (not here)      | [jr2804/sdo-skills](https://github.com/jr2804/sdo-skills)     | served by `sdo-skills-mcp`, never copied        |
| Skills server          | [jr2804/sdo-skills-mcp](https://github.com/jr2804/sdo-skills-mcp) | `catalog.toml`, `profiles/*.toml`, `sdo_list_skills`, `sdo_read_skill` |
| Test suite             | `tests/`                                                        | `test_*.py`, `conftest.py`                      |
| Project metadata       | `pyproject.toml`                                                | `[project]`, `[tool.pytest.ini_options]`        |
| Linter/formatter       | `ruff.toml`                                                     | Ruff rule selection, line length                |
| Structural sorter      | `.config/pyreorder.toml`                                         | `sections`, `strategies`, `hoist_inline_imports` |
| Type checker           | `ty.toml`                                                       | ty strictness                                   |
| Markdown linter        | `.config/rumdl.toml`                                            | `line-length`, `flavor`, disabled rules         |
| mise tasks             | `.config/mise/config.toml` + `.config/mise/conf.d/*.toml`       | `[tasks.dev]`, `[tasks.test]`, ...              |
| Copier answers         | `.copier-answers.yml`                                           | Template version + answers (regenerated)        |
| Pre-commit config      | `.pre-commit-config.yaml`                                       | Hook list                                       |

## Naming conventions

- **Repository name** (`project_slug`): kebab-case (`my-project`)
- **Python package** (`package_slug`): snake_case (`my_project`)
- **Layout**: `src/sdo_writer/`
- **Test files**: `test_<module>.py`
- **Template files** (in source template): `filename.ext.jinja` - the `.jinja`
  suffix is stripped on generation
- **Skill identifiers**: kebab-case, 1-64 characters, matching the directory
  name (`sdo-writing`, `etsi-procedures`)
- **Profile identifiers**: kebab-case, matching the TOML file name (`etsi`,
  `3gpp`, `itut`)
- **Agent name**: `sdo-writer`, rendered to `agents/sdo-writer.md`
