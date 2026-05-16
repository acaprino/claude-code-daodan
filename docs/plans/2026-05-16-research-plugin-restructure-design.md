# Research Plugin — Restructure Design

**Date:** 2026-05-16
**Scope:** The 2 agents in the `research` plugin (deep-researcher, quick-searcher) and their orchestration contract.
**Source of truth:** [`docs/references/agent-teams-best-practices.md`](../references/agent-teams-best-practices.md).
**Status:** Design only.

## Trigger

During the agent-teams research task that produced the best-practices reference, the `research:deep-researcher` agent was spawned with the correct prompt and refused to do the work, claiming: "Looking at my tools, I only have `Read` exposed. ... I cannot spawn quick-searcher sub-agents." Yet its frontmatter declares `tools: Agent, Read`. The orchestrator returned a long apology and refused to retry.

This is the single most important bug in the plugin: the orchestrator advertises itself as the entry point for any multi-source research, then bails on its first real invocation. Until fixed, the safe answer is "do not use deep-researcher; do the search inline" — which defeats the plugin.

## Root cause hypotheses

Three competing explanations. The plan should investigate each before applying a fix.

### H1: Sub-agent tool propagation issue (harness)

When an outer agent (e.g., the user-facing Claude) spawns `deep-researcher` via the Agent tool, and `deep-researcher`'s body tells it to spawn yet another agent (`quick-searcher`) via Agent, the harness may not propagate the Agent tool to the inner level. Nested spawning would be blocked.

Evidence supporting H1: the agent-teams documentation explicitly states "No nested teams. Teammates cannot spawn their own teams or teammates." Although deep-researcher is NOT a teammate (it's a subagent), the same restriction may apply to subagents-spawning-subagents.

Evidence against H1: the agent's frontmatter declares `tools: Agent, Read`, which suggests the SDK intends to expose Agent at the deep-researcher level. The agent did not report a "permission denied"; it reported the tool not being available at all.

### H2: System prompt self-restriction

The agent's body never names the Agent tool explicitly. It says: "you ... spawn parallel `research:quick-searcher` sub-agents", and "For each activated angle, spawn one `research:quick-searcher` via the `Agent` tool. Launch them in a single message with multiple tool calls."

Sonnet/Opus, given a goal but no explicit tool-call template, can decide the tool is "not available" if the body does not show the exact JSON shape of the call. This is a known failure mode when the body describes the WHAT but not the HOW.

Evidence supporting H2: the agent's apology starts with "Looking at my tools, I only have `Read` exposed", which is exactly what a model would say if it scanned its visible tool descriptions and didn't see the Agent tool used in any example.

### H3: Frontmatter-runtime mismatch

The plugin loader may not honor `tools: Agent, Read` correctly. This is the least likely (no other plugin reports the issue) but worth verifying.

## Diagnostic plan

Before applying any fix:

1. **Reproduce on a minimal example.** Create a tiny test agent `tmp-test-spawner` with `tools: Agent` and a body that says "use the Agent tool to spawn a `general-purpose` sub-agent". Spawn it. Observe whether it can call Agent.
2. **Check the SDK docs.** Look at https://platform.claude.com/docs/en/agent-sdk/subagents (already in the reference's source list) for any documented restriction on nested Agent tool use.
3. **Read the `general-purpose` agent body** to see if it has any explicit "spawn via Agent tool" example. If it does, that's a known-good pattern to mirror.

## Proposed fix (assuming H2 is at least partly responsible)

### Fix 1: Make the tool call explicit in the body

Rewrite the workflow section of `deep-researcher.md` to include an exact tool-call template. Example new prose:

> ## Phase 2: Spawn sub-agents in parallel
>
> Use the `Agent` tool with `subagent_type: "research:quick-searcher"`. Launch all activated angles in a single message with multiple Agent tool calls so they run concurrently.
>
> Concrete call shape for each angle:
>
> ```
> Agent({
>   subagent_type: "research:quick-searcher",
>   description: "Search angle A: authoritative",
>   prompt: "[the spawn prompt template below]"
> })
> ```

This removes any room for the model to wonder whether the tool is callable.

### Fix 2: Add WebSearch + WebFetch as fallback tools

Today `deep-researcher` cannot do web work at all — it's pure orchestration. If sub-agent spawning fails (H1, sub-agent-spawned-from-sub-agent harness restriction), the orchestrator has nowhere to go and must bail. The community pattern for resilient orchestrators is "delegate by default, fall back to first-person when delegation is not available".

Proposed `tools: Agent, Read, WebSearch, WebFetch` plus a body section "Fallback: direct mode":

> If the Agent tool is unavailable for sub-agent spawning (this can happen when you are yourself spawned as a sub-agent), fall back to direct mode: execute the activated angles yourself, one per round, using WebSearch and WebFetch with the per-angle budget. Cap your direct-mode budget at the equivalent of one sub-agent (5 WebSearch + 3 WebFetch per angle).

This preserves the value of the agent in the nested-spawn case at the cost of more tokens in that path.

### Fix 3: Improve the failure mode

If both delegation and fallback fail, the agent should return a structured error indicating which mechanism failed, not a free-form apology. Example:

> ## Failure response
>
> If you cannot spawn sub-agents AND cannot use WebSearch/WebFetch, return exactly this structured response:
>
> ```
> ## Research failed
> - Reason: <one line>
> - Tools attempted: <list>
> - Recommended fallback: invoke `research:quick-searcher` directly, or use `WebSearch` from the calling agent.
> ```

### Fix 4: quick-searcher hardening

`quick-searcher` is largely fine (`tools: Read, WebFetch, WebSearch, Bash`, sonnet model for cost). One small improvement: in **sub-unit mode**, the budget line in the prompt should be acknowledged in the output. Add to the output format:

```
## Sub-unit metadata
- Budget assigned: <as received>
- Budget used: ~N WebSearch + M WebFetch
- Exit reason: completed / budget-exhausted / target-not-found
```

This lets the deep-researcher detect partial completions and route around them.

## Out of scope

- The `research:web-search-techniques` skill is shared between the two agents and is upstream-derived; no changes proposed.
- The `general-purpose` agent's Agent tool semantics are a Claude Code framework concern, not a plugin concern. If the diagnostic reveals H1 (harness restriction), the fix is to document it in the deep-researcher body and accept the fallback path, not to lobby for an SDK change.

## Estimated impact

- 2 agent files modified (`deep-researcher.md`, `quick-searcher.md`)
- Plugin version bump: research 2.6.1 → 2.7.0 (minor: new tool dependencies and fallback path)
- Marketplace metadata: bump in the consolidated cycle with other restructures

## Risks

- **Direct mode in deep-researcher inflates its token usage.** The whole point of deep-researcher was orchestration overhead-only. Adding direct mode reverses that. Mitigation: cap direct mode at 1-angle budget equivalent and document it as a fallback, not a default.
- **WebSearch/WebFetch in an orchestrator is a code smell.** True, but it's a pragmatic resilience fix until the nested-Agent issue is understood. If H1 is invalidated, we can remove Fix 2 in a follow-up.
- **quick-searcher metadata could be ignored.** If deep-researcher does not actually read sub-agent outputs verbatim (it summarizes), the metadata section may not surface. Mitigation: state the metadata in the structured fields, not in free-form prose, so synthesis preserves them.

## Open questions

- **Is `research:deep-researcher` ever invoked as a top-level agent (user-typed), or only as a sub-agent spawned by another orchestrator like `/agent-teams:team-research`?** Affects whether H1 is even hit in practice. If top-level invocation is the norm, H2 is the more likely cause.
- **Should we add a smoke test?** This repo has no test infrastructure, but a `docs/plans/2026-05-16-research-smoke-test.md` describing a manual reproduction recipe would be useful for future regressions.

## Next step

1. Run the diagnostic plan (Section "Diagnostic plan") to localize H1 vs H2 vs H3.
2. Based on the diagnosis, write `2026-05-16-research-plugin-restructure-plan.md` selecting which fixes apply.
3. Apply the chosen fixes; verify by re-running the original research task that exposed the bug (best-practices for agentic teams).
