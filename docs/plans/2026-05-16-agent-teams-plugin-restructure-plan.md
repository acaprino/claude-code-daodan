# Agent Teams Plugin — Restructure Plan

**Date:** 2026-05-16
**Design doc:** [`2026-05-16-agent-teams-plugin-restructure-design.md`](2026-05-16-agent-teams-plugin-restructure-design.md)
**Status:** Ready to apply.

## Files modified

- `plugins/agent-teams/agents/team-lead.md`
- `plugins/agent-teams/agents/team-reviewer.md`
- `plugins/agent-teams/agents/team-implementer.md`
- `plugins/agent-teams/agents/team-debugger.md`
- `.claude-plugin/marketplace.json` (version bump)

## Edits

### `team-lead.md`

1. **Add Prime Directives section** at the top of the body, immediately after the H1 intro paragraph and before `## Core Mission`. Five numbered rules:

   ```markdown
   ## Prime Directives

   1. **Delegate. Never implement.** The lead does not edit files, run tests, or write code. If the user asks you to do something a teammate can do, decompose and assign. Activate delegate mode on yourself if necessary.
   2. **Every spawn prompt declares ownership.** A teammate prompt without an explicit "You own: <paths>" line is malformed. Two teammates editing the same file is your bug, not theirs.
   3. **Every artifact-producing spawn prompt declares its output path.** If the teammate writes a report or finding, the path goes in the spawn prompt. Returned text without an on-disk file is a fallback, not the contract.
   4. **Bound the team budget.** Plan for 3-10x the tokens of a single Claude (typical ~7x). Start with 2-3 teammates; scale up only when each teammate owns 5+ independent tasks.
   5. **Pick specialized agents over generics.** Use the Ecosystem Integration table below to select the most specialized agent for each role. The generic team-reviewer/team-implementer/team-debugger are fallbacks.
   ```

2. **Fix stale `broadcast` guidance.** Replace the `Communication Protocols` block (lines 70-77 in the pre-edit file):

   - Old: `2. Use \`broadcast\` only for critical team-wide announcements`
   - New: `2. Broadcast is no longer supported. To reach multiple teammates, send one message per recipient by name.`

3. **Tighten team size guidance** in `### Team Composition`:

   - Old: `Select optimal team size based on task complexity (2-5 teammates)`
   - New: `Pick the smallest team that fits the task. Default 2-3 teammates; 4-5 only when each teammate owns 5+ independent tasks. Beyond 5, coordination overhead grows faster than productivity.`

4. **Add Quality Gates section** after `## Team Lifecycle Protocol`:

   ```markdown
   ## Quality Gates via Hooks

   When the team produces work that must pass a check before merging or releasing, configure native hooks rather than babysitting:

   - `TeammateIdle` — exit code 2 returns the teammate to work with feedback. Use when a teammate marks itself idle but the work is not actually finished.
   - `TaskCreated` — exit code 2 blocks task creation. Use to enforce that every task description includes ownership and acceptance criteria.
   - `TaskCompleted` — exit code 2 blocks completion. Use to gate lint / type-check / test before a task closes.

   Hooks turn "trust and hope" into "trust and verify". Reference: `docs/references/agent-teams-best-practices.md` § Hooks for quality gates.
   ```

### `team-reviewer.md`

1. **Add scope budget rule** in a new `## Scope Budget` section after `## Review Dimensions`:

   ```markdown
   ## Scope Budget

   If after ~15 file reads you have not surfaced a finding in your assigned dimension, the scope is too broad or the dimension is not relevant to this target. Stop, output a "no findings — scope appears off-topic for this dimension" report, and return. Do not invent findings to fill space.
   ```

2. **Add Cross-Reviewer Notes** to the output format. Append to the existing output-format code block (after the `Recommended Fix` line):

   ```markdown

   ## Cross-Reviewer Notes (optional)

   If during analysis you spot an issue clearly belonging to another reviewer's dimension, list it here with `file:line` and a one-line description. Phase 3 consolidation routes these to the appropriate reviewer.
   ```

### `team-implementer.md`

1. **Strengthen Phase 1 (Understand Assignment).** Replace:

   - Old: `- Read your task description thoroughly`
   - New: `- Read your task description thoroughly. If the description does not list explicit owned files / directories, stop and message the lead before starting. Implementation on undeclared scope creates merge conflicts.`

2. **Emphasize TaskUpdate completion.** Replace Phase 5 step:

   - Old: `- Mark your task as completed via TaskUpdate`
   - New: `- Always call \`TaskUpdate(completed)\` BEFORE messaging the lead about completion. Tasks left in \`in_progress\` block dependent work and waste teammates' tokens.`

### `team-debugger.md`

1. **Add `Write` to tools** in frontmatter:

   - Old: `tools: Read, Glob, Grep, Bash`
   - New: `tools: Read, Write, Glob, Grep, Bash`

2. **Promote negative-results reporting** in Step 7. Replace:

   - Old: `- Deliver structured report to team lead`
   - New: `- Deliver structured report to team lead. Falsified hypotheses are valuable findings, not failures — report them with the same diligence as confirmed ones. A confidently disproven theory removes ambiguity for the lead.`

3. **Add Output Persistence section** at the end of the file (matching the pattern from reviewer agents). Append after the last line:

   ```markdown

   ## Output Persistence

   When you are spawned by a pipeline command that gives you an output file path in the prompt, write your final structured report to that path using the `Write` tool. Do not return the report only as message text. The orchestrator relies on the file being on disk for consolidation. If no path is provided, return the report inline as usual.
   ```

4. **Add sub-spawning caveat** to `## Ecosystem Integration` (lines 80-107). Append a closing paragraph:

   ```markdown

   ### Sub-spawning caveat

   When you spawn a specialized sub-agent (e.g., `senior-review:ui-race-auditor`) via the `Agent` tool, that sub-agent itself cannot spawn further sub-agents (Claude Agent SDK restriction). If your hypothesis requires deeper delegation than one level, report this to the team lead rather than trying to chain agents indirectly. The team lead has the team-level view to decide whether to re-spawn at the top level or escalate to the user.
   ```

## Version bumps

| Plugin | Before | After | Reason |
|---|---|---|---|
| `agent-teams` | 2.9.4 | 2.10.0 | Minor: 4 agents touched, behavior changes (team-lead Prime Directives, new Quality Gates section, broadcast removal) |
| Marketplace `metadata.version` | 6.8.2 | 6.8.3 | Patch: one plugin bumped, no global API change |

## Validation

- `grep` for any leftover `broadcast` references in `team-lead.md` after the edit.
- Re-read all four agent files end-to-end to verify section ordering still flows.
- Validate `marketplace.json` JSON syntax.
- No automated tests in repo (markdown-only project).

## Commit message

```
Restructure agent-teams plugin: 4 agents aligned with best-practices reference (v2.10.0)

Applies the design from docs/plans/2026-05-16-agent-teams-plugin-restructure-design.md
to the four agents in the plugin.

team-lead: adds a top-level Prime Directives section (delegate-never-implement,
mandatory ownership in every spawn prompt, output path declaration, team-size
discipline, specialized-agent preference). Replaces stale broadcast guidance
(the broadcast option was removed from SendMessageTool). Adds Quality Gates
section pointing at TeammateIdle / TaskCreated / TaskCompleted hooks.
Tightens team-size guidance from "2-5" to "2-3 default, up to 5".

team-reviewer: adds Scope Budget (stop after ~15 file reads if no finding)
and Cross-Reviewer Notes optional output section.

team-implementer: strengthens Phase 1 (stop if owned files are not declared)
and Phase 5 (TaskUpdate before message-to-lead, not after).

team-debugger: adds Write tool to allow persisting reports to disk,
plus an Output Persistence section matching the pattern just rolled out to
reviewers. Promotes negative-results reporting visibility. Adds a
sub-spawning caveat noting the SDK one-level subagent nesting limit.

Plan: docs/plans/2026-05-16-agent-teams-plugin-restructure-plan.md
Reference: docs/references/agent-teams-best-practices.md
```
