# Senior-Review Reviewers — Restructure Design

**Date:** 2026-05-16
**Scope:** The 10 reviewer agents that participate in `/agent-teams:team-review` Phase 2.
**Source of truth:** [`docs/references/agent-teams-best-practices.md`](../references/agent-teams-best-practices.md).
**Status:** Design only. Output Persistence and `Write` tool were already added in the previous turn; this captures the remaining gaps.

## Reviewers in scope

| Reviewer | Plugin | Specialization |
|---|---|---|
| `security-auditor` | senior-review | OWASP/CWE, attack scenarios |
| `code-auditor` | senior-review | Architecture, patterns, scoring |
| `logic-integrity-auditor` | senior-review | Contracts, invariants, domain rules |
| `ui-race-auditor` | senior-review | Async/timing UI bugs |
| `cleanup-auditor` | senior-review | Dead code, assets, VCS, deps |
| `distributed-flow-auditor` | senior-review | Cross-service flows |
| `chicken-egg-detector` | senior-review | Startup cycles |
| `react-performance-optimizer` | react-development | React 19 perf |
| `platform-reviewer` | platform-engineering | SPA/PWA/mobile/desktop rules |
| `team-reviewer` | agent-teams | Generic fallback (testing, API, migration, etc.) |

## What we already fixed (prev turn)

- All 10 now have an explicit `## Output Persistence` section.
- 3 had restrictive `tools:` and got `Write` added (cleanup-auditor, platform-reviewer, team-reviewer).
- Marketplace versions bumped (senior-review 5.6.1, platform-engineering 1.2.1, agent-teams 2.9.4, react-development 1.9.3, metadata 6.8.1).

## Remaining gaps vs. reference

### Gap 1: Scope budget guidance missing

The production lesson is explicit: token blowup most often comes from a reviewer spending 10-20 turns wandering the codebase before producing findings. Currently, no reviewer has an explicit "if you exceed N file reads without producing a finding, stop and report unclear scope" rule.

**Affected:** all 10 reviewers.

**Proposed addition** (one-liner in each reviewer's analysis methodology section):

> If after ~15 file reads you have not surfaced a finding in your dimension, the scope is too broad or the dimension is not relevant to this target. Stop, write a "no findings — scope appears off-topic for this dimension" report, and return.

### Gap 2: Interconnect-map anchor citation not mandated

Only `logic-integrity-auditor` requires every finding to cite an interconnect-map anchor. The other reviewers can read `.team-review/02-interconnect.md` (Phase 2 prompt tells them about it) but their system prompt does not penalize ignoring it.

The reference says findings that cite interconnect anchors are higher-quality because they survive Phase 3 deduplication better and prove the reviewer used the cross-component context.

**Affected:** 9 reviewers (all except `logic-integrity-auditor`).

**Proposed addition:** A line in each reviewer's "Output Format" or "PRIME DIRECTIVES" that says:

> When a finding maps to a contract, invariant, or assumption documented in `.team-review/02-interconnect.md`, cite the anchor (e.g., "Map anchor: ## Contracts -> Order-fulfillment idempotency"). Findings citing map anchors are tracked as a quality metric by the pipeline.

Not mandatory for findings that are purely local (a stylistic issue, a missing null check) — only for findings that touch cross-component logic.

### Gap 3: Cross-reviewer non-duplication policy

A reviewer may notice an issue outside their dimension (e.g., the security auditor spots a performance issue, or the cleanup auditor spots an architectural smell). Today the convention is "stay in lane", which loses signal.

**Affected:** all 10 reviewers.

**Proposed addition:** A `## Cross-Reviewer Notes` optional section at the end of every reviewer's output format:

> If during your analysis you spot an issue that clearly belongs to a different dimension, do not silently drop it. Add a "Cross-Reviewer Notes" section at the end of your output listing the off-dimension observations with `file:line` and a one-line description. Phase 3 consolidation routes these to the appropriate reviewer.

### Gap 4: "No findings" reporting honesty

`team-reviewer` has the Behavioral Trait "Reports 'no findings' dimensions honestly rather than inflating results". The specialized reviewers have similar guidance scattered ("Trivial diff = 0 findings is fine. Do NOT invent" in code-auditor, "Trivial changes may have 0 issues. Do NOT invent flaws to meet a quota" in security-auditor, etc.).

This is consistent but the language drifts between reviewers. Standardize it.

**Affected:** all 10 reviewers.

**Proposed addition:** A short shared "No-Findings Protocol" section:

> If your dimension genuinely has no findings on this target, output a one-line report stating so plus a list of what you examined. Do not invent findings to fill space. Reporting "examined X, Y, Z — no issues" is a valid, useful result.

### Gap 5: Tool-allowlist hygiene

Reviewers that inherit all tools by omitting `tools:` (7 of 10) can in principle call `Bash` with destructive commands. They shouldn't, by Prime Directive, but tightening the allowlist would be defense in depth.

**Affected:** 7 reviewers without explicit `tools:`.

**Proposed change:** Add `tools: Read, Write, Glob, Grep, Bash` explicitly to each — matching the existing 3 reviewers we just standardized. This makes the security posture uniform and reviewable in the frontmatter alone.

**Risk:** if a reviewer needed a tool we did not declare (e.g., `Edit`), it would lose that capability. Reviewers should not be editing code, so this is intentional, but verify case-by-case.

### Gap 6: Reviewer-specific knowledge-base reload

Each reviewer's body has a `## KNOWLEDGE BASE` section instructing it to load `defect-taxonomy` references. The instruction is consistent but the file lists are not — some reviewers say "always load X", others say "load on demand". Not a bug, but inconsistent UX for someone reading the agent.

**Affected:** 10 reviewers.

**Proposed:** No mandatory change. Leave per-reviewer judgment in place; just document the convention in this design so the eventual refactor doesn't accidentally homogenize them. Reviewers with clear always-load references (security, logic-integrity) should keep them; reviewers with discretionary loads (code-auditor, distributed-flow) should keep their "load by domain" model.

## Out of scope

- **Severity scale unification.** Each reviewer uses CRITICAL / HIGH / MEDIUM / LOW with reviewer-specific calibration (e.g., security weights at 2×, code-auditor floor at 1). Phase 3 of `/team-review` already calibrates across reviewers using the `agent-teams:multi-reviewer-patterns` skill. Do not change per-reviewer severity rules here.
- **Output schema.** Each reviewer has its own structured output format. They are diverse for a reason (security needs CWE + attack scenario; ui-race needs T0→T1 timelines). Do not unify the schemas.

## Cross-cutting changes

- Add Gap 1 (scope budget) to all 10 reviewers. ~3 lines per file.
- Add Gap 3 (Cross-Reviewer Notes section) to all 10 output formats. ~5 lines per file.
- Add Gap 4 (no-findings protocol) to all 10 reviewers. ~3 lines per file.
- Add Gap 2 (interconnect anchor citation) to 9 reviewers. ~3 lines per file.
- Add Gap 5 (explicit `tools:` allowlist) to 7 reviewers without it.

Total: ~30 lines per file × 10 files = ~300 lines of additions, distributed across 4 plugins.

## Estimated impact

- 10 agent files modified
- Plugin bumps: senior-review 5.6.1 → 5.7.0 (minor: behavior change in 7 reviewers), platform-engineering 1.2.1 → 1.2.2 (patch: small additions), agent-teams 2.9.4 → 2.9.5 (patch: team-reviewer touched), react-development 1.9.3 → 1.9.4 (patch: react-performance-optimizer touched)
- Marketplace metadata: bump after agent-teams design is applied (don't double-bump in one cycle)

## Risks

- **Reviewer prompt size grows.** Adding 30 lines to a 200-line agent is +15%. Token cost per reviewer invocation increases proportionally. Mitigation: written concisely, no boilerplate.
- **Consistency cost.** Five cross-cutting additions × 10 reviewers = 50 small edits, each is a possible typo. Mitigation: produce a single template block per gap and apply it via Edit with `replace_all` where unique; otherwise list each edit explicitly in the plan doc.
- **Phase 3 deduplication may need an update.** Adding Cross-Reviewer Notes creates new content that the `/team-review` Phase 3 (consolidation) doesn't yet route. Either Phase 3 ingests Cross-Reviewer Notes too (preferred) or it just preserves them in the final report. Both are acceptable; pick at plan time.

## Open questions

- Should we standardize on `## Output Persistence` being the LAST section in every reviewer (currently true after the previous turn's append), or move it nearer the top so the reviewer reads it before producing output? Practical answer: position doesn't matter if the reviewer reads its full system prompt; symbolic answer: top is more visible. Default: leave at end, the previous turn's choice.
- Should `cleanup-auditor` (which already produces a different output schema with D1/D2/D3/D4 dimensions and an FP-candidates table) follow the same Cross-Reviewer Notes pattern? Probably yes for consistency; verify at plan time.

## Next step

Approve this design (or amend), then produce `2026-05-16-senior-review-reviewer-restructure-plan.md` with: the exact templated additions per gap, the file-by-file Edit list, the frontmatter `tools:` updates, and the version-bump diff. Apply after the agent-teams plugin restructure is committed.
