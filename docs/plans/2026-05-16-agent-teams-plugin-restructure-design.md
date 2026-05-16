# Agent Teams Plugin — Restructure Design

**Date:** 2026-05-16
**Scope:** The 4 agents shipped by the `agent-teams` plugin (team-lead, team-implementer, team-reviewer, team-debugger).
**Source of truth:** [`docs/references/agent-teams-best-practices.md`](../references/agent-teams-best-practices.md).
**Status:** Design only. No code changes. Plan + execution to follow in a separate document.

## Context

The `agent-teams` plugin is upstream-synced from `wshobson/agents`. We have already overridden many areas (style, namespace, dash-aside rules) and added Output Persistence to `team-reviewer` in the previous turn. This design captures the remaining gaps between the agents' system prompts and the new best-practices reference, in the language they need to be rewritten in.

Three of the four agents (lead, implementer, debugger) have not been touched recently. The lead has stale guidance and is the most consequential agent in the plugin, because it shapes every team it spawns.

## Findings

### `team-lead.md`

**Stale guidance to fix:**

- `team-lead.md:73` says: "Use `broadcast` only for critical team-wide announcements". Per the May 2026 changelog, the broadcast option was **removed** from `SendMessageTool`. This line is now actively misleading; teams will burn turns trying to use a non-existent option. Replace with: "Send one message per recipient by name. Broadcast is no longer supported."
- `team-lead.md:23` says "Select optimal team size based on task complexity (2-5 teammates)". This is OK but does not call out the cost multiplier (3-10×) or the diminishing returns past 4-5 active agents. Worth tightening.

**Missing guidance (load-bearing):**

- **No instruction on delegate mode.** Production lesson #1: a capable Opus lead implements the first task itself while teammates sit idle. The lead's system prompt should explicitly tell the lead "do not implement; if the user asks you to implement, decompose and assign". This is partially covered by "Decomposes before delegating" in Behavioral Traits, but should be elevated to a Prime Directive.
- **No instruction on TaskCompleted hook usage.** The lead is in the position to set up hooks for the team. Add a "Quality Gates" section pointing to `TeammateIdle` / `TaskCreated` / `TaskCompleted` and explaining when each is appropriate.
- **No instruction on file ownership being declared in the spawn prompt itself.** The current "File Ownership Rules" section reads like a principle, not an operational rule. Make it explicit: "Every spawn prompt MUST include an explicit 'You own: <paths>' line."
- **No instruction on output-path delivery.** The lead is the one that, in pipeline commands like `/team-review`, must tell each reviewer where to write their report. Make this explicit: "When you spawn a teammate that produces a written artifact, include the output file path in the spawn prompt as 'Write your final report to <path>'."

**Decision: rewrite Prime Directives.** Lift these five rules out of Capabilities and Behavioral Traits and put them at the top of the agent body as a numbered Prime Directives section, so they cannot be overlooked.

### `team-reviewer.md`

Already updated with Output Persistence and `Write` tool. Two further improvements:

- **Scope budget guidance.** Add a one-liner: "If your assigned dimension requires more than ~15 file reads before producing findings, the scope is too broad. Report this back to the lead and stop." This addresses the 10-20-turn codebase-exploration anti-pattern documented in the reference.
- **Cross-reviewer non-duplication.** team-reviewer is the fallback for performance/testing/API/migration dimensions. Add a one-liner: "If your finding overlaps with another reviewer's dimension (e.g., a security issue you noticed while reviewing performance), surface it in a 'Cross-Reviewer Notes' section instead of dropping it; the lead deduplicates in Phase 3."

### `team-implementer.md`

Mostly fine. `tools` already includes `Write, Edit`. File ownership protocol is explicit. Minor improvements:

- **Add explicit scope bound.** Current Phase 1 says "Read your task description thoroughly". Add: "If the task description does not list explicit owned files, stop and ask the lead before starting. Implementation on undeclared scope creates merge conflicts."
- **Add TaskUpdate completion call out.** Phase 5 already says "Mark your task as completed via TaskUpdate" — good. Make it more emphatic: "Always call `TaskUpdate(completed)` BEFORE messaging the lead about completion. Tasks left in `in_progress` block dependent work and waste teammates' tokens."

### `team-debugger.md`

Read-only by design (`tools: Read, Glob, Grep, Bash`). Output is a structured report. Minor improvements:

- **Output Persistence.** Apply the same pattern just rolled out to reviewers: if the spawner provides an output path, write the structured report to disk with the `Write` tool. Requires adding `Write` to `tools`.
- **Confidence calibration on negative results.** Current Step 6 distinguishes confidence levels but does not say "report falsified hypotheses with the same diligence as confirmed ones". The Behavioral Traits section says "Reports negative results (falsified hypotheses) as valuable findings" — promote this to the body of Step 7 (Report Findings) for visibility.
- **Sub-spawning warning.** Lines 86-87 instruct using `research:deep-researcher` via Agent tool. Given the deep-researcher bug surfaced in turn N (it claimed to not have the Agent tool), this guidance is currently fragile. Add: "If the spawned sub-agent fails to use a tool it should have, report this back to the lead rather than retrying with a different agent. The lead has the team-level view to decide whether to re-spawn or escalate to the user."

## Cross-cutting changes

- **Add a "Prime Directives" structural section** at the top of all four agents (team-lead, team-implementer, team-reviewer, team-debugger), 4-7 numbered rules each, lifted from the most load-bearing rules below in the file. Pattern already used in `senior-review` reviewers.
- **Standardize "Output Persistence"** as a shared section name across team-reviewer (done), team-implementer (NA — modifies code directly), team-debugger (to do), team-lead (NA — coordinator).
- **Frontmatter `description`:** all four agents already have TRIGGER WHEN / DO NOT TRIGGER WHEN. Verify they still match how the lead picks specialized agents from the Ecosystem Integration table; in particular, the team-reviewer DO NOT TRIGGER list should call out: "do not use when a specialized senior-review agent matches the dimension".

## Out of scope for this design

- The `agent-teams` skills (`parallel-feature-development`, `parallel-debugging`, `multi-reviewer-patterns`, `task-coordination-strategies`, `team-communication-protocols`, `team-composition-patterns`) are upstream-synced and have separate evolution. A skill restructure can follow if needed; this design focuses on the four agents.
- The `agent-teams` commands (`team-feature`, `team-design`, `team-review`, `team-debug`, `team-codebase-map`, `team-research`, `team-shutdown`, `team-status`, `team-spawn`, `team-delegate`) are pipeline glue, not agents. Their reviewer-prompt templates were already touched in the previous turn (team-review Phase 2). Other commands may have similar template gaps, but they need to be analyzed per command, not under "agent restructure".

## Estimated impact

- 4 agent files modified
- Plugin version bump: 2.9.4 → 2.10.0 (minor: behavior change in lead instructions)
- Marketplace metadata: 6.8.1 → 6.8.2
- Tests: none in repo (markdown-only project). Validation = manual re-read + spot-check with `/agent-teams:team-review` on a small target.

## Risks

- **The lead becomes too directive.** Adding 5 prime directives makes the lead system prompt larger and more opinionated. Mitigation: write directives in imperative terse style, keep total prime directives section ≤ ~25 lines.
- **Upstream drift increases.** Each new override moves us further from `wshobson/agents` upstream. Mitigation: document every override in commit messages and in the CLAUDE.md sync notes.
- **Conflicting guidance with `agent-teams:team-composition-patterns` skill.** The skill describes team sizing; the lead now repeats some of that. Mitigation: the agent body should reference the skill, not duplicate it.

## Open questions

- Do we want to enforce that the lead loads `team-composition-patterns` and `multi-reviewer-patterns` skills at startup? Currently a Behavioral Trait. Could be stronger.
- Should `team-debugger` learn the `deep-dive-analysis` skill as a standard tool, or keep it as an optional escalation?

## Next step

Approve this design (or amend), then produce `2026-05-16-agent-teams-plugin-restructure-plan.md` with the exact Edit operations, frontmatter changes, and version-bump diff.
