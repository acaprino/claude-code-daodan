# Claude Code Daodan

The Daodan is the symbiote that augments its host. This repository is the Daodan of Claude Code: a marketplace of agents, skills, and commands that augment the base model into a specialized toolkit covering development workflows, code quality, AI tooling, scraping, trading, observability, and more. Remote: `acaprino/claude-code-daodan` on GitHub.

## Project structure

```
.claude-plugin/
  marketplace.json          # plugin registry (versions, metadata)
plugins/
  <plugin-name>/
    agents/                 # agent .md files (frontmatter + system prompt)
    skills/                 # skill directories (SKILL.md + optional references/)
    commands/               # slash-command .md files
    hooks/                  # hook handlers (JS/Python) + hooks.json (acp-hooks, prompt-improver)
```

43 plugins: clean-code, deep-dive-analysis, tauri-development, frontend, react-development, xterm, ai-tooling, python-development, stripe, system-utils, messaging, research, business, project-setup, app-analyzer, typescript-development, csp, digital-marketing, senior-review, obsidian-development, browser-extensions, learning, marketplace-ops, playwright-skill, acp-hooks, prompt-improver, cc-usage, codebase-mapper, git-worktrees, rag-development, docs, testing, platform-engineering, ibkr-trading, mt5-trading, opentelemetry, docker, grabber-development, agent-teams, reverse-engineering, codebase-cleanup, libgdx-development, kotlin-development.

## Plugin anatomy

**Agents** - Markdown files with YAML frontmatter:
- `name`: agent identifier (kebab-case)
- `description`: when/how to use the agent (use YAML multiline `>` for long descriptions)
- `model`: LLM model (default: `opus`)
- `tools` (optional): comma-separated tool list (e.g. `Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch, Task`); omit to allow all tools
- `color`: UI accent color (one of: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`)
- Body: terse keyword-list style system prompt; simple agents ~50-200 lines, complex agents up to ~700 lines

**Skills** - Directory with `SKILL.md` (frontmatter: `name`, `description`) and optional supplementary subdirs: `references/` (docs), `scripts/`, `templates/`, `assets/`, `lib/`.

**Commands** - Slash-command `.md` files with YAML frontmatter (`description`, `argument-hint`) and usage instructions/examples.

**Hooks** - Used by `acp-hooks` and `prompt-improver` plugins. Contains `hooks.json` (hook definitions) and `handlers/` directory with JS handler scripts. `acp-hooks` also uses `plugins/acp-hooks/.claude-plugin/plugin.json` for supplementary hook configuration alongside marketplace registration.

## Conventions

- Agent names: kebab-case matching the filename (e.g. `quick-searcher.md`)
- Plugin names: kebab-case directory names
- Default model: `opus` (latest Claude Opus); exceptions noted per-agent (e.g. `quick-searcher` uses `sonnet`)
- Agent body style: terse keyword lists, imperative tone, structured with markdown headers
- Skills supplementary subdirs: `references/`, `scripts/`, `templates/`, `assets/`, `lib/` as needed
- No build step or runtime framework - plugins are markdown with optional helper scripts (Python, JS) in skills' `scripts/` subdirs
- Avoid the dash-aside construct anywhere (code, comments, commit messages, documentation). The rule targets the *rhetorical pattern* of bracketing a clause between dashes, in any form: `—` (em dash), `--` (double hyphen), or ` - ` (spaced hyphen). All three are banned when used to wrap a parenthetical aside (e.g., "lorem ipsum -- lorem ipsum -- lorem ipsum"). Substituting `--` for `—` is **not** the fix. Rewrite into separate sentences, parentheses, colons, or just delete the aside. Hyphenated compounds (`file-ownership`, `multi-agent`) are unrelated and fine.

## Marketplace update workflow

When changes modify plugins (agents, skills, commands), update the marketplace **before committing**:

1. **Bump plugin version** - increment `version` for the changed plugin in `.claude-plugin/marketplace.json`
2. **Bump marketplace version** - increment `metadata.version` in the same file
3. **Commit together** - stage both the plugin files and `marketplace.json` in one commit
4. **Push to remote** - `git push` to `master`

Key fields in `.claude-plugin/marketplace.json`:
- `metadata.version`: overall marketplace version
- `plugins[].version`: per-plugin version
- Install command: `claude plugin marketplace add acaprino/claude-code-daodan`

## Adding a new plugin

1. Create `plugins/<name>/` with `agents/`, `skills/`, `commands/`, and/or `hooks/` subdirectories as needed
2. Write agent/skill/command markdown files following existing patterns
3. Register the plugin in `.claude-plugin/marketplace.json` - add entry to `plugins[]` with `name`, `source`, `description`, `version` (start at `1.0.0`), `author`, `license`, `keywords`, `category`, `strict`, paths to agents/skills/commands, and optionally `dependencies`/`optionalDependencies` (arrays of plugin names)
4. Bump `metadata.version` and commit everything together

## Git workflow

- Single branch: `master`
- Commit style: imperative, descriptive (e.g. "Add high-value keywords to prompt-engineer agent")
- Primary workflow: direct push to master (PRs used occasionally)

## Build / CI

None. No tests, no build step, no CI pipeline. All content is static markdown.

## Documentation

`docs/plugins/` contains per-plugin documentation. `docs/plans/` holds implementation plans used by planning skills.

## External-repository intake

When the user asks to "import", "pull", "vendor", "cherry-pick", or "borrow from" an external GitHub repository (anything not already in the sync table below), follow this workflow before touching any local file. This section covers the *first* intake. Re-syncing repositories already registered uses the separate workflow under "Upstream-synced plugins" below.

### 1. Classify the operation

We do not fork, submodule, or add runtime dependencies. The only intake mode for this marketplace is **vendoring**: a one-shot or tracked copy of upstream content into our tree, with attribution preserved and the content adapted to our conventions.

| Sub-mode | When to pick | Example |
|---|---|---|
| **Full vendoring** | Upstream is a complete drop-in (a single SKILL.md, a small set of references) and there is no local equivalent | `playwright-skill` |
| **Cherry-pick vendoring** | Upstream has many files but only a subset adds value, or 23 commands collide with our existing namespace | `pbakaus/impeccable` (11 of 35 reference files imported, zero commands) |
| **Hybrid merge** | Upstream covers ground that overlaps with a local file; append upstream content as a delimited section instead of creating a duplicate | `pbakaus/impeccable` spatial-design merged into local `layout-patterns.md` |
| **Inspiration only** | We adopt patterns or workflow ideas but write our own content from scratch; no upstream text copied | `deep-dive-analysis` from `gsd-build/get-shit-done` |

Combinations are normal (Impeccable used cherry-pick + hybrid merge + new files in the same intake).

### 2. Decide the four dimensions

Before writing any file, lock down each dimension. State them back to the user via `AskUserQuestion` whenever a meaningful choice exists.

| Dimension | Question | Common answers |
|---|---|---|
| **Selection** | Full repo or cherry-pick? | Cherry-pick if upstream is large, has collisions, or carries unused infrastructure |
| **Merge** | Standalone new files or merged into existing local files? | Merge when overlap exists; standalone for orphan topics |
| **Sync strategy** | One-shot snapshot or ongoing sync? | Snapshot when upstream changes slowly or churn is unwanted; ongoing sync when upstream is actively maintained and aligned with our direction |
| **Tracking** | Register in the upstream-synced table or leave untracked? | Register only if "ongoing sync" was chosen; snapshots can still be registered for re-import convenience |

### 3. License compliance gate

Block before fetching:

1. Read the upstream `LICENSE` file. The four expected outcomes:
   - **MIT / BSD / ISC / Apache-2.0**: proceed; preserve attribution header in every derived file.
   - **MPL-2.0**: proceed for documentation-only content; flag to the user before importing source code.
   - **GPL-2.0 / GPL-3.0 / AGPL**: STOP. Ask the user explicitly; the marketplace is MIT and incompatible licensing must be a conscious decision.
   - **No license / proprietary**: STOP. Do not import.
2. For Apache-2.0 specifically, check whether upstream has a `NOTICE` file. If it does, preserve its contents alongside the derived files.
3. Attribution header on every derived file (new or merged section):
   ```
   <!--
   Portions of this file are derived from <owner>/<repo>
   (https://github.com/<owner>/<repo>), <SPDX-license> License.
   Snapshot YYYY-MM-DD.
   -->
   ```

### 4. Fetch and inspect (read-only)

Use `gh api repos/<owner>/<repo>/contents/<path>` with `--jq '.content' | base64 -d`. Save everything to `.upstream-scratch/<repo>/` (excluded from commits). Read every fetched file before writing local files. Count and assess size before proposing the merge plan.

### 5. Adapt to local conventions

Before saving any derived file, scan for and rewrite:

- **Dash-aside construct** ("X — Y — Z" / "X -- Y -- Z" / "X - Y - Z" bracketing a clause): replace with sentences, parentheses, or colons. Never substitute one dash form for another.
- **Emoji**: remove if the destination plugin's existing files have none.
- **Upstream-specific cross-references**: rewrite `[reference/foo.md](foo.md)` style links to point at the local destination path (or remove if the target was not imported). Rewrite `{{template_vars}}` and references to upstream-only commands.
- **Namespace prefixes**: rewrite `superpowers:X` -> `ai-tooling:X` and similar local namespace conventions.
- **Stale tool names** in agent-teams imports: `Teammate` -> `TeamCreate`, `Task tool to spawn` -> `Agent tool`.

### 6. Wire the new content into existing agents and commands

Importing content that no agent reads is wasted work. After saving derived files:

1. Add a `## References Library` (or equivalent) entry in the host plugin's `SKILL.md` that indexes every new/extended reference with a one-line topic description.
2. Update any command or agent that should now consult the new references. Add explicit `Read plugins/<plugin>/skills/.../<file>.md` instructions in the relevant prompt sections.
3. Avoid preloading discipline: the consumers must read references on-demand, not all upfront. State this in the wiring text.

### 7. Decide on tracking and re-sync

If the sub-mode is "ongoing sync" (or "snapshot but worth tracking for re-import"), append a row to the upstream-synced table below, with:
- Plugin (and sub-skill, if applicable) plus license tag for non-MIT sources
- Upstream repo plus the specific subpath
- Full list of derived local files and any merged sections

Then append the matching `gh api` fetch loop to the "How to sync a plugin" code block below. Do this even for snapshots; it makes a future re-import a one-command operation rather than archaeology.

If the sub-mode is "inspiration only", do NOT add a sync-table row. Add an inline note in the affected file describing what was adopted from where, but no sync entry.

### 8. Version bump and commit

- Bump every plugin whose `version` in `marketplace.json` had content added.
- Bump `metadata.version` (minor bump for first-time intake of a new upstream; patch bump for follow-up reworks of an existing intake).
- Single commit with the imported files, the local edits, the SKILL.md wiring, the CLAUDE.md sync-table update, and the version bumps together.
- Commit message: `Cherry-pick / Vendor / Import <subject> from <owner>/<repo> (v<new>)` with a short description block listing new files, merged sections, license, and attribution date.

### 9. Verification before push

- `grep` derived files for any leftover upstream-only references, stale tool names, or dash-aside constructs.
- Validate `marketplace.json` JSON syntax.
- `git status` shows nothing in `.upstream-scratch/` staged.
- `git diff --stat` to sanity-check scope.

---

## Upstream-synced plugins

Some plugins are ported from external repositories and should be kept in sync with their upstream source. When asked to update one of these plugins, fetch the latest content from the upstream URL using `gh api` and apply any changes, then follow the standard marketplace update workflow.

### Default upstream-update strategy

When the user asks for "upstream updates" (or similar), this is the default workflow. Do not blindly overwrite local files - most syncs need targeted merging because local has legitimate customizations.

1. **Check all synced plugins in parallel**. For each file in the sync table below, diff the upstream against the local version. Spawn Explore agents when there are many files to parallelize the diffing. Focus the reports on: which files differ, what changed, and whether the drift is intentional or worth pulling.

2. **Classify each file** before touching it:
   - **Clear win** - new upstream file missing locally, or a bug/fact fix with no local conflict. Pull directly.
   - **Minor refinement** - small wording/metadata changes. Pull if no local frontmatter or content conflicts.
   - **Hard merge** - upstream rewrote a section we also evolved locally. Layer upstream changes onto local; do not overwrite.
   - **Intentional drift** (do not touch) - local namespace rewrites (`superpowers:` -> `ai-tooling:`), local polish (typo fixes, expanded triggers), style conventions (no dash-aside construct per CLAUDE.md; no emojis in some plugins), local-only additions (custom presets, Ecosystem Integration sections, Context Sharing Pattern in `multi-reviewer-patterns`), upstream dash-asides rewritten to sentences/parens/colons.

3. **Preserve these local customizations** on every merge:
   - Source attribution lines at the top of files
   - Frontmatter: localized `description` (often multiline with `>`), `tools`, `color`, `version`, `model`
   - Plugin-specific style: no dash-aside construct (rewrite "X — Y — Z" / "X -- Y -- Z" / "X - Y - Z" asides into sentences, parens, or colons), no emojis in some plugins
   - Namespace replacements (`superpowers:X` -> `ai-tooling:X`)
   - Local-only sections (e.g., `## Ecosystem Integration` in agent-teams agents)

4. **For judgment calls**, ask the user via `AskUserQuestion`:
   - When upstream rewrote a section we also evolved (merge vs keep vs overwrite)
   - When upstream adds a feature that conflicts with local direction
   - When a file is flagged as "major drift"

5. **Apply targeted Edits, not Writes** - prefer surgical edits that fix specific bugs (stale tool names, added items in a list) over replacing whole files. Only use Write for new files or when the entire file is being replaced.

6. **Watch for stale tool names** (common drift source): `` `Teammate` tool `` / `` `Task` tool to spawn `` / `` Call `Teammate` cleanup `` / `` operation: "spawnTeam" `` -> fix to `` `TeamCreate` tool `` / `` `Agent` tool `` / `` `TeamDelete` ``. Grep all agent-teams files after any sync to catch these.

7. **Version bump and commit** - bump each touched plugin's `version` in `.claude-plugin/marketplace.json`, bump `metadata.version`, and commit everything together with a descriptive message like "Sync upstream updates for X and Y (vN.N.N)". Push to master.

8. **Verify** - run `Grep` for any remaining stale tool names, confirm marketplace.json is consistent, then `git status` / `git diff --stat` before committing.


| Plugin | Upstream source | Files to sync |
|--------|----------------|---------------|
| `ai-tooling` (brainstorming) | `obra/superpowers` - `skills/brainstorming/SKILL.md` | `plugins/ai-tooling/skills/brainstorming/SKILL.md` |
| `ai-tooling` (writing-plans) | `obra/superpowers` - `skills/writing-plans/SKILL.md` | `plugins/ai-tooling/skills/writing-plans/SKILL.md` |
| `ai-tooling` (executing-plans) | `obra/superpowers` - `skills/executing-plans/SKILL.md` | `plugins/ai-tooling/skills/executing-plans/SKILL.md` |
| `frontend` (frontend-css) | `paulirish/dotfiles` - `agents/skills/modern-css/SKILL.md` | `plugins/frontend/skills/frontend-css/SKILL.md`, `plugins/frontend/skills/frontend-css/references/argyle-cacadia-2025-deck.md` |
| `deep-dive-analysis` (inspiration) | `gsd-build/get-shit-done` - `agents/gsd-codebase-mapper.md` | `plugins/deep-dive-analysis/commands/deep-dive-analysis.md` (patterns adopted, not direct copy) |
| `playwright-skill` | `lackeyjb/playwright-skill` - `skills/playwright-skill/` | `plugins/playwright-skill/skills/playwright-skill/SKILL.md`, `plugins/playwright-skill/skills/playwright-skill/API_REFERENCE.md`, `plugins/playwright-skill/skills/playwright-skill/run.js`, `plugins/playwright-skill/skills/playwright-skill/package.json`, `plugins/playwright-skill/skills/playwright-skill/lib/helpers.js` |
| `react-development` (react-best-practices) | `vercel-labs/agent-skills` - `skills/react-best-practices/` | `plugins/react-development/skills/react-best-practices/SKILL.md`, `plugins/react-development/skills/react-best-practices/references.md`, `plugins/react-development/skills/react-best-practices/rules/*.md` |
| `digital-marketing` (domain-hunter) | `ReScienceLab/opc-skills` - `skills/domain-hunter/` | `plugins/digital-marketing/skills/domain-hunter/SKILL.md`, `plugins/digital-marketing/skills/domain-hunter/references/registrars.md`, `plugins/digital-marketing/skills/domain-hunter/references/spaceship-api.md` |
| `prompt-improver` | `severity1/claude-code-prompt-improver` | `plugins/prompt-improver/skills/prompt-improver/SKILL.md`, `plugins/prompt-improver/skills/prompt-improver/references/*.md`, `plugins/prompt-improver/hooks/handlers/improve-prompt.js` |
| `testing` (tdd) | `mattpocock/skills` - `skills/engineering/tdd/` | `plugins/testing/skills/tdd/SKILL.md`, `plugins/testing/skills/tdd/references/tests.md`, `plugins/testing/skills/tdd/references/deep-modules.md`, `plugins/testing/skills/tdd/references/mocking.md`, `plugins/testing/skills/tdd/references/interface-design.md`, `plugins/testing/skills/tdd/references/refactoring.md` |
| `docker` (multi-stage-dockerfile) | `github/awesome-copilot` - `skills/multi-stage-dockerfile/SKILL.md` | `plugins/docker/skills/multi-stage-dockerfile/SKILL.md` |
| `testing` (e2e-testing-patterns) | `wshobson/agents` - `plugins/developer-essentials/skills/e2e-testing-patterns/SKILL.md` | `plugins/testing/skills/e2e-testing-patterns/SKILL.md` |
| `agent-teams` | `wshobson/agents` - `plugins/agent-teams/` | `plugins/agent-teams/agents/*.md`, `plugins/agent-teams/commands/*.md`, `plugins/agent-teams/skills/*/SKILL.md`, `plugins/agent-teams/skills/*/references/*.md` |
| `senior-review` (semantic-interconnect-mapper) | `wshobson/agents` - `plugins/agent-orchestration/agents/context-manager.md` (pattern cherry-picked, not a direct copy) | `plugins/senior-review/agents/semantic-interconnect-mapper.md` |
| `typescript-development` (mastering-typescript) | `SpillwaveSolutions/mastering-typescript-skill` - `mastering-typescript/` | `plugins/typescript-development/skills/mastering-typescript/SKILL.md`, `plugins/typescript-development/skills/mastering-typescript/references/*.md`, `plugins/typescript-development/skills/mastering-typescript/scripts/validate-setup.sh`, `plugins/typescript-development/skills/mastering-typescript/assets/tsconfig-template.json`, `plugins/typescript-development/skills/mastering-typescript/assets/eslint-template.js` |
| `frontend` (impeccable cherry-pick, Apache-2.0) | `pbakaus/impeccable` - `skill/reference/` | New files: `plugins/frontend/skills/frontend-css/references/{typography,color-and-contrast,motion-design,heuristics-scoring,cognitive-load,personas}.md`, `plugins/frontend/skills/frontend-strategy/references/brand-register.md`. Merged sections (appended, delimited by attribution comment): `plugins/frontend/skills/frontend-css/references/{layout-patterns,ui-pattern-guide,css-patterns,ux-patterns}.md` |
| `frontend` (ui-ux-pro-max cherry-pick, MIT) | `nextlevelbuilder/ui-ux-pro-max-skill` - `.claude/skills/design-system/references/` | `plugins/frontend/skills/frontend-css/references/{token-architecture,primitive-tokens,semantic-tokens,component-tokens,component-specs,states-and-variants,tailwind-integration}.md` |
| `frontend` (NOTICE propagation, Apache-2.0 / MIT) | `pbakaus/impeccable` - `NOTICE.md` | `plugins/frontend/NOTICE.md` (consolidated upstream NOTICE chain: Impeccable -> Anthropic frontend-design + ehmo/typecraft-guide-skill, plus ui-ux-pro-max-skill MIT acknowledgement). The `ehmo/typecraft-guide-skill` lineage is also reflected in the attribution header of `plugins/frontend/skills/frontend-css/references/typography.md`. |
| `reverse-engineering` | `wshobson/agents` - `plugins/reverse-engineering/` | `plugins/reverse-engineering/agents/*.md` (firmware-analyst, malware-analyst, reverse-engineer), `plugins/reverse-engineering/skills/*/SKILL.md` (anti-reversing-techniques, binary-analysis-patterns, memory-forensics, protocol-reverse-engineering), `plugins/reverse-engineering/skills/anti-reversing-techniques/references/advanced-techniques.md` |
| `codebase-cleanup` (cherry-pick, MIT) | `wshobson/agents` - `plugins/codebase-cleanup/commands/` | `plugins/codebase-cleanup/commands/deps-audit.md`, `plugins/codebase-cleanup/commands/refactor-clean.md`, `plugins/codebase-cleanup/commands/tech-debt.md`. Upstream `agents/code-reviewer.md` and `agents/test-automator.md` intentionally NOT vendored (heavy overlap with local `senior-review/*` and `testing/*` coverage). Frontmatters rewritten to local style with TRIGGER WHEN / DO NOT TRIGGER WHEN routing notes, emojis stripped from `deps-audit.md`, license-description strings normalized to colon-separated form. |
| `kotlin-development` (full vendor, MIT) | `Jeffallan/claude-skills` - `skills/kotlin-specialist/` | `plugins/kotlin-development/skills/kotlin-specialist/SKILL.md`, `plugins/kotlin-development/skills/kotlin-specialist/references/{coroutines-flow,multiplatform-kmp,android-compose,ktor-server,dsl-idioms}.md`. Adaptation on sync: strip upstream extra frontmatter fields (`license`, `metadata.author`, `version`, `domain`, `triggers`, `role`, `scope`, `output-format`, `related-skills`); keep only `name` and `description` in local frontmatter; rewrite upstream single-paragraph `description` into local `description: >` multiline form with TRIGGER WHEN / DO NOT TRIGGER WHEN. Add MIT attribution header comment immediately after the frontmatter on SKILL.md and at the top of every reference file. Drop the upstream `[Documentation](https://jeffallan.github.io/...)` link at the bottom of SKILL.md. Single-connector em-dashes ("X — Y") in code comments are preserved as-is (they are NOT bracketed asides). |

### How to sync a plugin

```bash
# Fetch latest SKILL.md from upstream (obra/superpowers example)
gh api repos/obra/superpowers/contents/skills/brainstorming/SKILL.md \
  --jq '.content' | base64 -d

# Fetch latest SKILL.md from upstream (paulirish/dotfiles example)
# Local target: plugins/frontend/skills/frontend-css/SKILL.md and plugins/frontend/skills/frontend-css/references/argyle-cacadia-2025-deck.md
gh api repos/paulirish/dotfiles/contents/agents/skills/modern-css/SKILL.md \
  --jq '.content' | base64 -d

# Fetch latest gsd-codebase-mapper.md from upstream (gsd-build/get-shit-done example)
gh api repos/gsd-build/get-shit-done/contents/agents/gsd-codebase-mapper.md \
  --jq '.content' | base64 -d

# Fetch latest playwright-skill files from upstream (lackeyjb/playwright-skill example)
gh api repos/lackeyjb/playwright-skill/contents/skills/playwright-skill/SKILL.md \
  --jq '.content' | base64 -d
gh api repos/lackeyjb/playwright-skill/contents/skills/playwright-skill/run.js \
  --jq '.content' | base64 -d
gh api repos/lackeyjb/playwright-skill/contents/skills/playwright-skill/lib/helpers.js \
  --jq '.content' | base64 -d

# Fetch latest react-best-practices from upstream (vercel-labs/agent-skills example)
# Local target: plugins/react-development/skills/react-best-practices/
gh api repos/vercel-labs/agent-skills/contents/skills/react-best-practices/SKILL.md \
  --jq '.content' | base64 -d
gh api repos/vercel-labs/agent-skills/contents/skills/react-best-practices/AGENTS.md \
  --jq '.content' | base64 -d  # saved locally as references.md
# For rules: iterate all files in skills/react-best-practices/rules/

# Fetch latest domain-hunter files from upstream (ReScienceLab/opc-skills example)
# NOTE: Upstream Step 3 uses dedicated Twitter/Reddit Python scripts - replace with WebSearch
# queries targeting site:x.com and site:reddit.com when syncing
gh api repos/ReScienceLab/opc-skills/contents/skills/domain-hunter/SKILL.md \
  --jq '.content' | base64 -d
gh api repos/ReScienceLab/opc-skills/contents/skills/domain-hunter/references/registrars.md \
  --jq '.content' | base64 -d
gh api repos/ReScienceLab/opc-skills/contents/skills/domain-hunter/references/spaceship-api.md \
  --jq '.content' | base64 -d

# Fetch latest prompt-improver files from upstream (severity1/claude-code-prompt-improver example)
gh api repos/severity1/claude-code-prompt-improver/contents/skills/prompt-improver/SKILL.md \
  --jq '.content' | base64 -d
gh api repos/severity1/claude-code-prompt-improver/contents/skills/prompt-improver/references/question-patterns.md \
  --jq '.content' | base64 -d
gh api repos/severity1/claude-code-prompt-improver/contents/skills/prompt-improver/references/research-strategies.md \
  --jq '.content' | base64 -d
gh api repos/severity1/claude-code-prompt-improver/contents/skills/prompt-improver/references/examples.md \
  --jq '.content' | base64 -d
# NOTE: upstream uses Python (scripts/improve-prompt.py), local version is JS (hooks/handlers/improve-prompt.js)
gh api repos/severity1/claude-code-prompt-improver/contents/scripts/improve-prompt.py \
  --jq '.content' | base64 -d

# Fetch latest TDD skill files from upstream (mattpocock/skills example)
# Note: upstream restructured tdd/ under skills/engineering/tdd/ in 2026
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/SKILL.md \
  --jq '.content' | base64 -d
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/tests.md \
  --jq '.content' | base64 -d
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/deep-modules.md \
  --jq '.content' | base64 -d
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/mocking.md \
  --jq '.content' | base64 -d
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/interface-design.md \
  --jq '.content' | base64 -d
gh api repos/mattpocock/skills/contents/skills/engineering/tdd/refactoring.md \
  --jq '.content' | base64 -d

# Fetch latest multi-stage-dockerfile SKILL.md from upstream (github/awesome-copilot example)
gh api repos/github/awesome-copilot/contents/skills/multi-stage-dockerfile/SKILL.md \
  --jq '.content' | base64 -d

# Fetch latest e2e-testing-patterns SKILL.md from upstream (wshobson/agents example)
gh api repos/wshobson/agents/contents/plugins/developer-essentials/skills/e2e-testing-patterns/SKILL.md \
  --jq '.content' | base64 -d

# Fetch latest agent-teams files from upstream (wshobson/agents example)
# Agents
for agent in team-lead team-reviewer team-debugger team-implementer; do
  gh api "repos/wshobson/agents/contents/plugins/agent-teams/agents/$agent.md" \
    --jq '.content' | base64 -d
done
# Commands
for cmd in team-spawn team-review team-debug team-feature team-delegate team-status team-shutdown; do
  gh api "repos/wshobson/agents/contents/plugins/agent-teams/commands/$cmd.md" \
    --jq '.content' | base64 -d
done
# Skills (SKILL.md + references/)
for skill in multi-reviewer-patterns parallel-debugging parallel-feature-development task-coordination-strategies team-communication-protocols team-composition-patterns; do
  gh api "repos/wshobson/agents/contents/plugins/agent-teams/skills/$skill/SKILL.md" \
    --jq '.content' | base64 -d
  # List and fetch references
  gh api "repos/wshobson/agents/contents/plugins/agent-teams/skills/$skill/references" \
    --jq '.[].name' | while read ref; do
    gh api "repos/wshobson/agents/contents/plugins/agent-teams/skills/$skill/references/$ref" \
      --jq '.content' | base64 -d
  done
done

# Fetch upstream context-manager as reference for semantic-interconnect-mapper (pattern only, not direct copy)
# Local target: plugins/senior-review/agents/semantic-interconnect-mapper.md
gh api repos/wshobson/agents/contents/plugins/agent-orchestration/agents/context-manager.md \
  --jq '.content' | base64 -d

# Fetch latest mastering-typescript files from upstream (SpillwaveSolutions/mastering-typescript-skill example)
# Local target: plugins/typescript-development/skills/mastering-typescript/
gh api repos/SpillwaveSolutions/mastering-typescript-skill/contents/mastering-typescript/SKILL.md \
  --jq '.content' | base64 -d
# References
for ref in type-system generics enterprise-patterns react-integration nestjs-integration toolchain; do
  gh api "repos/SpillwaveSolutions/mastering-typescript-skill/contents/mastering-typescript/references/$ref.md" \
    --jq '.content' | base64 -d
done
# Scripts and assets
gh api repos/SpillwaveSolutions/mastering-typescript-skill/contents/mastering-typescript/scripts/validate-setup.sh \
  --jq '.content' | base64 -d
gh api repos/SpillwaveSolutions/mastering-typescript-skill/contents/mastering-typescript/assets/tsconfig-template.json \
  --jq '.content' | base64 -d
gh api repos/SpillwaveSolutions/mastering-typescript-skill/contents/mastering-typescript/assets/eslint-template.js \
  --jq '.content' | base64 -d

# Fetch latest Impeccable reference files from upstream (pbakaus/impeccable, Apache-2.0)
# Local targets:
#   - plugins/frontend/skills/frontend-css/references/ (new files: typography, color-and-contrast,
#     motion-design, heuristics-scoring, cognitive-load, personas)
#   - plugins/frontend/skills/frontend-strategy/references/brand-register.md (renamed from upstream `brand.md`)
#   - Merged appended sections (delimited by attribution comment) inside
#     plugins/frontend/skills/frontend-css/references/{layout-patterns,ui-pattern-guide,css-patterns,ux-patterns}.md
#     fed by upstream {spatial-design, interaction-design, responsive-design, ux-writing}.md respectively.
# Apache-2.0: preserve the attribution comment at the top of each derived file or section.
for ref in typography color-and-contrast spatial-design motion-design interaction-design responsive-design ux-writing heuristics-scoring cognitive-load personas brand; do
  gh api "repos/pbakaus/impeccable/contents/skill/reference/$ref.md" \
    --jq '.content' | base64 -d
done

# Fetch latest UI/UX Pro Max design-system deliverable references (nextlevelbuilder/ui-ux-pro-max-skill, MIT)
# Local targets: plugins/frontend/skills/frontend-css/references/{token-architecture,primitive-tokens,semantic-tokens,component-tokens,component-specs,states-and-variants,tailwind-integration}.md
# MIT: preserve the attribution comment at the top of each derived file.
# Skipped intentionally: main ui-ux-pro-max SKILL.md (overlaps with our local content),
# brand sub-skill (we have brand-register.md from Impeccable), slide-generation system (out of scope),
# CSV catalogs in src/ui-ux-pro-max/data/ (bloat, not documentation), CLI scripts (no runtime).
for ref in token-architecture primitive-tokens semantic-tokens component-tokens component-specs states-and-variants tailwind-integration; do
  gh api "repos/nextlevelbuilder/ui-ux-pro-max-skill/contents/.claude/skills/design-system/references/$ref.md" \
    --jq '.content' | base64 -d
done

# Fetch latest NOTICE.md from Impeccable (Apache-2.0 4(d) attribution propagation)
# Local target: plugins/frontend/NOTICE.md (consolidates the upstream attribution chain
# for Impeccable, Anthropic frontend-design, ehmo/typecraft-guide-skill, and ui-ux-pro-max-skill).
gh api repos/pbakaus/impeccable/contents/NOTICE.md \
  --jq '.content' | base64 -d

# Fetch latest reverse-engineering plugin files from upstream (wshobson/agents example)
# Local target: plugins/reverse-engineering/
# MIT: preserve the attribution comment immediately after the YAML frontmatter in each file.
for agent in firmware-analyst malware-analyst reverse-engineer; do
  gh api "repos/wshobson/agents/contents/plugins/reverse-engineering/agents/$agent.md" \
    --jq '.content' | base64 -d
done
for skill in anti-reversing-techniques binary-analysis-patterns memory-forensics protocol-reverse-engineering; do
  gh api "repos/wshobson/agents/contents/plugins/reverse-engineering/skills/$skill/SKILL.md" \
    --jq '.content' | base64 -d
done
gh api "repos/wshobson/agents/contents/plugins/reverse-engineering/skills/anti-reversing-techniques/references/advanced-techniques.md" \
  --jq '.content' | base64 -d

# Fetch latest codebase-cleanup commands from upstream (wshobson/agents example, MIT cherry-pick)
# Local target: plugins/codebase-cleanup/commands/
# MIT: preserve the attribution comment immediately after the YAML frontmatter in each file.
# Skipped intentionally: agents/code-reviewer.md and agents/test-automator.md
#   (heavy overlap with senior-review/code-auditor + security-auditor + code-review,
#   and with testing/tdd + python-development/python-tdd; vendoring them would create
#   duplicate routing).
# Adaptation on sync: rewrite the upstream single-line `description:` into the local
# `description: >` multiline form with TRIGGER WHEN / DO NOT TRIGGER WHEN sections,
# strip emojis from `deps-audit.md`, and normalize license-description strings
# (`'Copyleft - requires source code disclosure'` -> `'Copyleft: requires source code disclosure'`).
for cmd in deps-audit refactor-clean tech-debt; do
  gh api "repos/wshobson/agents/contents/plugins/codebase-cleanup/commands/$cmd.md" \
    --jq '.content' | base64 -d
done

# Fetch latest kotlin-specialist files from upstream (Jeffallan/claude-skills, MIT full vendor)
# Local target: plugins/kotlin-development/skills/kotlin-specialist/
# MIT: preserve the attribution comment immediately after the YAML frontmatter on SKILL.md
# and at the top of every reference file.
# Adaptation on sync: strip upstream extra frontmatter fields (license, metadata.author,
# version, domain, triggers, role, scope, output-format, related-skills); keep only
# `name` and `description` in local frontmatter; rewrite the upstream single-paragraph
# `description` into local `description: >` multiline form with TRIGGER WHEN /
# DO NOT TRIGGER WHEN routing. Drop the upstream `[Documentation](https://jeffallan.github.io/...)`
# link at the bottom of SKILL.md. Preserve single-connector em-dashes ("X — Y") inside
# code comments (they are NOT bracketed asides; the dash-aside rule does not apply).
gh api repos/Jeffallan/claude-skills/contents/skills/kotlin-specialist/SKILL.md \
  --jq '.content' | base64 -d
for ref in coroutines-flow multiplatform-kmp android-compose ktor-server dsl-idioms; do
  gh api "repos/Jeffallan/claude-skills/contents/skills/kotlin-specialist/references/$ref.md" \
    --jq '.content' | base64 -d
done
```

Then compare with the local file, apply upstream changes while preserving local additions (source attribution line at top of each file), bump the plugin version, bump `metadata.version`, and commit + push.

**Important:** Upstream superpowers skills reference other superpowers skills we don't have (e.g. `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:subagent-driven-development`). When syncing, replace `superpowers:` skill references with either our local `ai-tooling:` equivalents or generic guidance describing the same action. Keep `docs/plans/` path (not upstream's `docs/superpowers/plans/`).

---

## Custom plugin maintenance

A "custom plugin" is any plugin NOT listed in the "Upstream-synced plugins" table above. Its content is hand-authored or research-grounded and has no upstream source to re-pull. The list is large (libgdx-development, ibkr-trading, mt5-trading, rag-development, opentelemetry, stripe, csp, grabber-development, browser-extensions, obsidian-development, business, research, codebase-mapper, frontend agents, python-development, typescript-development, senior-review, digital-marketing, docs, learning, app-analyzer, project-setup, marketplace-ops, system-utils, cc-usage, git-worktrees, platform-engineering, testing, react-development, tauri-development, messaging, xterm, clean-code, deep-dive-analysis, ai-tooling agents/skills not from upstream, acp-hooks). If a plugin is not in the sync table, it falls under this section.

Custom plugins decay differently than vendored ones. There is no upstream commit to diff against. Versions, framework recommendations, breaking-change notes, and "current as of 2026" claims become stale silently. The maintenance protocol below is the antidote.

### Freshness risk classes

Classify each plugin into one of four classes. The class determines refresh cadence and triage priority.

| Class | What it tracks | Typical cadence | Examples |
|---|---|---|---|
| **Very fast** | Versions bump every few months; breaking changes are common; ecosystem reshuffles | Every 3 months | rag-development (embedding models, rerankers, vector DBs), digital-marketing/ga4-implementation (Consent Mode, GA4 events), react-development (React 19, Vercel guidance) |
| **Fast** | Framework releases 2-3x per year; APIs evolve | Every 6 months | libgdx-development, opentelemetry, tauri-development, stripe (API additions, webhook event types), grabber-development (anti-bot vendor moves), browser-extensions |
| **Moderate** | Major releases ~yearly; breaking changes rare | Every 12 months | ibkr-trading, mt5-trading, csp (OR-Tools), python-development, typescript-development, messaging (RabbitMQ majors), obsidian-development |
| **Slow** | Workflow knowledge that ages by behavior change, not version bumps | Opportunistic; review only when symptoms appear | senior-review, codebase-mapper, agent-teams workflows, ai-tooling skills, project-setup, marketplace-ops, system-utils, cc-usage, git-worktrees, learning, docs, research, business, clean-code, frontend (the agent side), deep-dive-analysis, platform-engineering, testing methodology, xterm, app-analyzer, acp-hooks |

If unsure, default to "Fast" (6 months). Reclassify after the first refresh based on how much actually changed.

### Where hard-coded versions hide

Predictable hot spots, in priority order:

1. **Agent body** -- "Core Knowledge" / "Library Landscape" sections list package names and versions
2. **SKILL.md** -- "Quick Start" steps name install commands with versions
3. **References** -- changelog / breaking-changes sections; benchmark numbers; "as of YYYY" lines
4. **Audit command** -- checklists referencing specific version-gated features
5. **Marketplace.json description** -- if the description name-drops versions (e.g. "RabbitMQ 4.x coverage")

The agent and SKILL.md are the highest-value targets per minute of refresh effort. Reference files matter less for typical users (progressively disclosed) but matter most for power users.

### Update protocol

Steps to refresh a custom plugin. Same protocol regardless of risk class; only the cadence differs.

1. **Re-research the domain** with `research:deep-researcher`. Use angles A (Authoritative) + D (Recency) at minimum. Prompt template:
   ```
   Angles: A + D
   Query: <framework> current version, breaking changes since <version-in-plugin>,
   recommended baseline versions of dependencies, deprecations, ecosystem changes.
   Focus: facts that would change recommendations in an existing knowledge base.
   ```
   Optional: add angle B (Community) if real-world usage patterns are part of what you cover.

2. **Diff the findings against the plugin**. Spawn Explore agents to grep the plugin for the specific version strings and section titles that came up in research. For each, decide:
   - **Clear win**: outdated fact with a confirmed replacement, apply Edit
   - **Subtle shift**: framework changed defaults but old approach still works, mention both
   - **No change**: research confirmed our content is still accurate
   - **Open question**: research was inconclusive, leave a comment and revisit next cycle

3. **Surgical Edits only**. Do not rewrite whole files. Replace specific lines and sentences. Preserve structure so future refreshes have stable anchors.

4. **Bump versions**. Patch bump for fact updates (`1.2.3 -> 1.2.4`). Minor bump if a new section, file, or reference was added (`1.2.3 -> 1.3.0`). Always bump `metadata.version` too (patch is fine unless the marketplace shape itself changed).

5. **Commit with a refresh tag**. Format:
   ```
   Refresh <plugin-name> for <framework> v<new-version> (v<plugin-version>)
   ```
   This makes the git log a searchable record of which plugins got attention when. Use this to decide what to refresh next: anything not touched in a full risk-class cadence is overdue.

### Triage on demand

When you sit down to do a refresh pass and don't know where to start:

```bash
# Plugins not refreshed in the last 6 months
git log --since="6 months ago" --name-only --pretty=format: -- plugins/ \
  | grep -v "^$" | awk -F/ '{print $2}' | sort -u > /tmp/recently-touched.txt

# Compare against the full plugin list in marketplace.json. The difference is your work queue.
```

Refresh the "Very fast" and "Fast" classes first if any are on the work queue; defer "Moderate" and "Slow" classes unless something specific prompted the review.

### When to upgrade a custom plugin to upstream-synced

If during a refresh you discover that someone else's open-source repo now publishes content that overlaps significantly with one of our custom plugins, evaluate vendoring it instead of maintaining from scratch. Follow the "External-repository intake" workflow in this file, then move the plugin's row from this section's mental model into the "Upstream-synced plugins" sync table.
