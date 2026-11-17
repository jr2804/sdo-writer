---
title: Usage
---

## Usage

The install gives you one agent and a connection to a skills server. The agent decides which skills
to load; you decide what to write.

### Starting a session

```bash
opencode
```

Then ask for the document you need, in the words of your body:

```text
Draft an ETSI contribution for the next 3GPP/ETSI workshop, agenda item 7.6.
```

```text
Write a change request for TS 38.331, adding a new IE to the measurement gap report.
```

```text
Draft the ITU-T Recommendation text for study group 13, clause 5.
```

The agent lists the skills, picks the drafting skill, the procedure skill and the writing style
skill, and works from the document skeleton rather than from a blank page.

### What the agent does

The agent file is generated from the profile. It carries a short set of non-negotiables:

- A **contribution** and a **deliverable** are different things. The agent does not present one as the other.
- **Rules come from the skills.** When a question touches the Directives, the IPR policy, a numbering
  rule or a document structure, the agent reads the skill that holds the rule instead of answering
  from memory.
- **The skeleton is the starting point.** Deliverable skeletons live in the skill assets. They are filled, not rebuilt.
- **The checklist runs before "done".** Each document type has a checklist; the agent works through it and says what it could not verify.
- **The tool is pulled on demand.** OfficeCLI and the other tools are fetched through `mise` the first time they are needed.

### Reading a skill

The skills arrive over MCP, not from a directory. Two tools do the work:

```text
sdo_list_skills()                     # name, description and file count of every skill
sdo_read_skill("etsi-procedures")     # the SKILL.md text, or one reference file
sdo_read_skill("etsi-procedures", "references/approval-routes.md")
```

You do not have to call them yourself; the agent does when it picks a skill. It is worth watching
once, though: if a name in the routing table does not appear in the list, the profile is serving
fewer skills than you expect.

### Working with a document

A typical session follows this shape:

1. **Scope.** Which body, which document type, which agenda item or work item, which meeting.
2. **Read.** The agent loads the rules that apply and tells you which ones it used.
3. **Draft.** The skeleton is copied into the working directory and filled through OfficeCLI, so the styles, the numbering and the headers survive.
4. **Check.** The checklist of the document type is applied, and the result is reported.

You can interrupt at any point. The agent keeps the document in the project, not in a hidden place.

### Where the working files go

The `sdo-project-setup` skill sets up a project directory:

```text
<project>/
├── PLAN.md          # what the document is, and what it must contain
├── AGENTS.md        # the local contract for the agents that work here
├── <doc-id> - <title>.docx
├── figures/         # images, at least 300 dpi
├── ref/             # source material
├── scripts/         # helper scripts
└── tmp/             # scratch space
```

The point of `PLAN.md` is that the plan holds the content decisions, so the document can be regenerated without repeating the questions.

### Asking for something specific

| Request | Skills that answer it |
| ------- | --------------------- |
| "How does an ETSI contribution get approved?" | `etsi-procedures` |
| "What does the ETSI IPR policy require of me?" | `sdo-ipr`, `etsi-directives` |
| "What is the numbering of ITU-T clauses?" | `itut-reference` |
| "Which working group owns feature X?" | `3gpp-working-groups` |
| "How do I write a 3GPP change request?" | `3gpp-change-request` |
| "Rewrite this paragraph in standards prose" | `sdo-writing` |
| "Add a table to this document without breaking the styles" | `sdo-docx` |
| "Create the document skeleton for an ETSI TS" | `sdo-drafting` |
| "Fetch the latest version of ETSI TS 103 224" | `etsi-tools` |

### Tooling

The skills never assume a tool is installed. They use mise to fetch it:

```bash
mise x github:iOfficeAI/OfficeCLI -- officecli get file.docx
mise x uv -- uv run scripts/build_schedule.py
```

If mise is missing, the skills say so and name the tool they needed. That is deliberate: a missing
tool should be a clear message, not a confusing failure three steps later.

### When the server does not start

The agent's first tool call fails if `sdo-skills-mcp` cannot start. Check the command by hand:

```bash
sdo-writer entry --profile etsi
```

That prints the exact `command` array from your configuration. Run it: it starts the server on stdio
and waits for a request, so interrupt it once you see that it did not fail. The usual causes are no
network on the first run and a `--root` that points at a directory without skills.

The command pins the interpreter (`--python 3.14`) on purpose: the regular, GIL-enabled CPython
build. `fastmcp` pulls `pywin32` on Windows, which has no free-threading wheel, so a machine whose
default interpreter is a free-threaded build fails to resolve the server with
`pywin32 … has no wheels with a free-threading compatible ABI tag`. The pin makes `uvx` pick — or
download — the regular 3.14 build instead. Change it only if you know the server installs into
another interpreter.
