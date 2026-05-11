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

39 plugins: clean-code, deep-dive-analysis, tauri-development, frontend, react-development, xterm, ai-tooling, python-development, stripe, system-utils, messaging, research, business, project-setup, app-analyzer, typescript-development, csp, digital-marketing, senior-review, obsidian-development, browser-extensions, learning, marketplace-ops, playwright-skill, acp-hooks, prompt-improver, cc-usage, codebase-mapper, git-worktrees, rag-development, docs, testing, platform-engineering, ibkr-trading, mt5-trading, opentelemetry, docker, grabber-development, agent-teams.

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
```

Then compare with the local file, apply upstream changes while preserving local additions (source attribution line at top of each file), bump the plugin version, bump `metadata.version`, and commit + push.

**Important:** Upstream superpowers skills reference other superpowers skills we don't have (e.g. `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:subagent-driven-development`). When syncing, replace `superpowers:` skill references with either our local `ai-tooling:` equivalents or generic guidance describing the same action. Keep `docs/plans/` path (not upstream's `docs/superpowers/plans/`).
