---
description: "Debug issues using competing hypotheses with parallel investigation by multiple agents"
argument-hint: "<error-description-or-file> [--hypotheses N] [--scope files|module|project]"
---

# Team Debug

Debug complex issues using the Analysis of Competing Hypotheses (ACH) methodology. Multiple debugger agents investigate different hypotheses in parallel, gathering evidence to confirm or falsify each one.

## Skills to Load

Before starting, invoke these skills (via the `Skill` tool) to inform the debugging process. They are **skills, not agents** -- never pass them as `subagent_type` to `Agent`/`TeamCreate`:
- `agent-teams:parallel-debugging` -- hypothesis generation framework, evidence standards, arbitration protocol
- `senior-review:defect-taxonomy` -- defect classification with CWE mappings for categorizing findings
- `deep-dive-analysis:deep-dive-analysis` -- systematic codebase analysis for initial triage
- `agent-teams:team-communication-protocols` -- message type selection, shutdown protocol

## Pre-flight Checks

1. Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set
2. Parse `$ARGUMENTS`:
   - `<error-description-or-file>`: description of the bug, error message, or path to a file exhibiting the issue
   - `--hypotheses N`: number of hypotheses to generate (default: 3)
   - `--scope`: investigation scope -- `files` (specific files), `module` (module/package), `project` (entire project)

## Phase 1: Initial Triage

1. Analyze the error description or file:
   - If file path: read the file, look for obvious issues, collect error context
   - If error description: search the codebase for related code, error messages, stack traces
2. Identify the symptom clearly: what is failing, when, and how
3. Gather initial context: recent git changes, related tests, configuration

## Phase 2: Hypothesis Generation

Generate N hypotheses about the root cause, covering different failure mode categories:

1. **Logic Error** -- Incorrect algorithm, wrong condition, off-by-one, missing edge case
2. **Data Issue** -- Invalid input, type mismatch, null/undefined, encoding problem
3. **State Problem** -- Race condition, stale cache, incorrect initialization, mutation bug
4. **Integration Failure** -- API contract violation, version mismatch, configuration error
5. **Resource Issue** -- Memory leak, connection exhaustion, timeout, disk space
6. **Environment** -- Missing dependency, wrong version, platform-specific behavior

Present hypotheses to user: "Generated {N} hypotheses. Spawning investigators..."

## Phase 3: Investigation

1. Use `TeamCreate` tool to create the team with `team_name: "debug-{timestamp}"` and `description`
2. For each hypothesis, use `Agent` tool to spawn a teammate:
   - `name`: `investigator-{n}` (e.g., "investigator-1")
   - `subagent_type`: "agent-teams:team-debugger"
   - `prompt`: Include the hypothesis, investigation scope, and relevant context
3. Use `TaskCreate` for each investigator's task:
   - Subject: "Investigate hypothesis: {hypothesis summary}"
   - Description: Full hypothesis statement, scope boundaries, evidence criteria

## Phase 4: Evidence Collection

1. Monitor TaskList for completion
2. As investigators complete, collect their evidence reports
3. Track: "{completed}/{total} investigations complete"

## Phase 5: Arbitration

1. Compare findings across all investigators:
   - Which hypotheses were confirmed (high confidence)?
   - Which were falsified (contradicting evidence)?
   - Which are inconclusive (insufficient evidence)?

2. Rank confirmed hypotheses by:
   - Confidence level (High > Medium > Low)
   - Strength of causal chain
   - Amount of supporting evidence
   - Absence of contradicting evidence

3. Present root cause analysis:

   ```
   ## Debug Report: {error description}

   ### Root Cause (Most Likely)
   **Hypothesis**: {description}
   **Confidence**: {High/Medium/Low}
   **Evidence**: {summary with file:line citations}
   **Causal Chain**: {step-by-step from cause to symptom}

   ### Recommended Fix
   {specific fix with code changes}

   ### Other Hypotheses
   - {hypothesis 2}: {status} -- {brief evidence summary}
   - {hypothesis 3}: {status} -- {brief evidence summary}
   ```

4. Branch on arbitration outcome:
   - **At least one Confirmed (High confidence)** → skip Phase 6, proceed to Phase 7
   - **No Confirmed but ≥1 Plausible/Inconclusive that runtime data could disambiguate** → proceed to Phase 6
   - **No Confirmed and no Plausible** → report failure to user, ask for additional context, optionally return to Phase 2 with new hypotheses

## Phase 6: Targeted Log Injection (conditional)

Run only when Phase 5 arbitration is inconclusive and runtime evidence would disambiguate. Skip otherwise.

1. Identify the 3-5 most informative observation points across the surviving hypotheses (function entries, before/after async boundaries, conditional branches, catch blocks).
2. Spawn one `team-debugger` (or the appropriate specialized investigator) with prompt: "Inject `[DEBUG]` logs at the following locations: {list}. Do not modify behavior. Use the Runtime Evidence Pattern from `agent-teams:parallel-debugging`."
3. Use the canonical log format from the `parallel-debugging` skill:
   ```
   [DEBUG] [{file}:{line}] {description} { {vars} }
   ```
4. Report injection summary to the user with a per-location purpose table, then prompt: "Reproduce the bug and paste the console output."
5. Treat the user's pasted output as new evidence. Return to Phase 5 with the surviving hypotheses re-arbitrated against the runtime data.
6. Cap iterations at 2 rounds of log injection. If still inconclusive, escalate to the user with a written summary of what was ruled out and what would be needed next.

## Phase 7: Fix Proposal & Verification

1. Present the minimal fix in diff format with the confidence score of the confirmed hypothesis.
2. Ask the user to approve before applying.
3. After applying, ask the user to reproduce the original failure.
4. Branch on result:
   - **Fixed** → proceed to Phase 8
   - **Not fixed** → return to Phase 2 (hypothesis generation) carrying the new negative evidence; the previously "confirmed" hypothesis becomes Falsified

## Phase 8: Cleanup

Two cleanup actions, in order:

1. **Debug log cleanup** (only if Phase 6 ran):
   - Grep for the prefix across modified files. For JS/TS:
     ```bash
     grep -rn '\[DEBUG\]' . --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx'
     ```
     For other languages, swap the `--include` globs accordingly.
   - Remove every matched line. Report the count: "Removed {N} debug logs from {file count} files."
2. **Team teardown**:
   - Send `shutdown_request` to all investigators
   - Call `TeamDelete` to remove team resources
