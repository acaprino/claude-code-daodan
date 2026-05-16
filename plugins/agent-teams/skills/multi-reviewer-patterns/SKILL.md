---
name: multi-reviewer-patterns
description: >
  Coordinate parallel code reviews across multiple quality dimensions with finding
  deduplication, severity calibration, and consolidated reporting. Use this skill
  when organizing multi-reviewer code reviews, calibrating finding severity, or
  consolidating review results.
version: 1.2.0
---

# Multi-Reviewer Patterns

Patterns for coordinating parallel code reviews across multiple quality dimensions, deduplicating findings, calibrating severity, and producing consolidated reports.

## When to Use This Skill

- Organizing a multi-dimensional code review
- Deciding which review dimensions to assign
- Deduplicating findings from multiple reviewers
- Calibrating severity ratings consistently
- Producing a consolidated review report

## Review Dimension Allocation

### Available Dimensions

| Dimension         | Focus                                   | When to Include                             |
| ----------------- | --------------------------------------- | ------------------------------------------- |
| **Security**      | Vulnerabilities, auth, input validation | Always for code handling user input or auth |
| **Performance**   | Query efficiency, memory, caching       | When changing data access or hot paths      |
| **Architecture**  | SOLID, coupling, patterns               | For structural changes or new modules       |
| **Testing**       | Coverage, quality, edge cases           | When adding new functionality               |
| **Accessibility** | WCAG, ARIA, keyboard nav               | For UI/frontend changes                     |

### Recommended Combinations

| Scenario               | Dimensions                                   |
| ---------------------- | -------------------------------------------- |
| API endpoint changes   | Security, Performance, Architecture          |
| Frontend component     | Architecture, Testing, Accessibility         |
| Database migration     | Performance, Architecture                    |
| Authentication changes | Security, Testing                            |
| Full feature review    | Security, Performance, Architecture, Testing |

## Context Sharing Pattern

When `/team-review` runs in pipeline mode (no `--skip-interconnect`), reviewers do not receive raw code only -- they receive two context artifacts produced in Phase 1:

1. **Deep-dive output** at `.deep-dive/` (from `deep-dive-analysis` plugin): `01-structure.md`, `02-interfaces.md`, `05-risks.md`, and optionally `03-flows.md`, `04-semantics.md`, `06-documentation.md`, `07-final-report.md`.
2. **Interconnect map** at `.team-review/02-interconnect.md` (from `senior-review:semantic-interconnect-mapper`): contracts (formal / structural / implicit), invariants, domain rules, assumptions (verified / documented / unverified), integration hot-spots, change impact radius.

### Why context sharing matters

Without shared context, each reviewer re-reads the code from scratch. This is wasteful and, more importantly, blinds them to bugs that only manifest across components -- broken implicit contracts, invariant drift, bypass paths, non-idempotent retries, terminal state mutations. Phase 1 surfaces those concerns in the interconnect map, and Phase 2 reviewers use the map as a checklist.

### How reviewers should consume the context

Reviewers should **not** read the entire context file. They should Grep or read only the anchors relevant to their dimension, guided by the `## Reviewer Hints` section at the bottom of `.team-review/02-interconnect.md`.

Default anchor routing:

| Reviewer dimension | Primary anchors in interconnect map |
|--------------------|-------------------------------------|
| security | `## Integration Hot-Spots` (inbound), `## Assumptions` (unverified), `## Contracts` (implicit, input validation) |
| architecture (code-auditor) | `## Invariants`, `## Contracts` (structural + implicit), `## Call Graph` |
| logic-integrity | `## Contracts` (implicit, unverified), `## Invariants`, `## Assumptions` (unverified), `## Domain Rules` |
| distributed-flows | `## Integration Hot-Spots` (HTTP / queue / IPC), `## Call Graph` (cross-service) |
| chicken-egg | `## Assumptions` (initialization order), `## Integration Hot-Spots` (Env / config), `## Invariants` (cross-component) |
| ui-races | `## Invariants` (temporal), `## Integration Hot-Spots` (UI state) |
| api-contracts (future) | `## Contracts` (formal) |

### Prompt template for context-aware reviewers

```
You are reviewing for the {dimension} dimension.

## Target
[...]

## Diff
[...]

## Context files
- Deep-dive output: .deep-dive/
- Interconnect map: .team-review/02-interconnect.md

Per `## Reviewer Hints` in the interconnect map, focus your reading on these anchors:
{anchors-for-this-dimension}

## Instructions
Follow your agent definition's phases and output format. Cite file:line for every finding.
Every finding that relates to a contract/invariant/assumption in the interconnect map should
also cite the map anchor that surfaced the concern.

Write your output to .team-review/findings-{dimension}.md.
```

### Quality metric: context utilization rate

A useful quality signal at the end of a review: **what fraction of findings cite an interconnect-map anchor?**

- High (>= 30%): reviewers are leveraging the context effectively; the pipeline is paying off.
- Medium (10-30%): context used but inconsistently; consider refining prompts.
- Low (< 10%): either reviewers are ignoring the map or the map is too generic to be actionable.

The logic-integrity-auditor dimension should be at >= 70% (its findings are almost entirely driven by the map).

### Fallback: `--skip-interconnect` mode

When the pipeline is skipped, reviewers receive only target + diff. In this mode:
- `logic-integrity-auditor` is not spawned (no map to drive it).
- All other reviewers fall back to their pre-pipeline behavior.
- No `.deep-dive/` or `.team-review/02-interconnect.md` references should appear in reviewer prompts.

## Pipeline Conventions (per reviewer)

Every reviewer agent that runs as part of `/team-review` Phase 2 carries a `## Pipeline Conventions` section in its system prompt with four cross-cutting rules. The orchestrator does not need to repeat them in the spawn prompt, but should be aware of what they mandate:

- **Scope budget**: each reviewer stops after ~15 file reads without a finding and returns a "scope-off-topic" report. The orchestrator should plan targets at a granularity that respects this budget.
- **No-findings protocol**: reviewers may legitimately return "examined X, Y, Z -- no issues" instead of inventing findings. Treat such reports as valid Phase 3 input, not failure.
- **Cross-Reviewer Notes**: reviewers append observations that belong to other dimensions in a `## Cross-Reviewer Notes` section. Phase 3 consolidation must scan for this section and route the observations to the appropriate reviewer (or surface them in the consolidated report under the recipient dimension).
- **Interconnect anchor citation**: reviewers cite map anchors when applicable. This is the same signal as the context utilization rate above; the section below quantifies the quality metric.

Reference: `docs/references/agent-teams-best-practices.md` § Pipeline Conventions.

## Finding Deduplication

When multiple reviewers report issues at the same location:

### Merge Rules

1. **Same file:line, same issue** -- Merge into one finding, credit all reviewers
2. **Same file:line, different issues** -- Keep as separate findings
3. **Same issue, different locations** -- Keep separate but cross-reference
4. **Conflicting severity** -- Use the higher severity rating
5. **Conflicting recommendations** -- Include both with reviewer attribution

### Deduplication Process

```
For each finding in all reviewer reports:
  1. Check if another finding references the same file:line
  2. If yes, check if they describe the same issue
  3. If same issue: merge, keeping the more detailed description
  4. If different issue: keep both, tag as "co-located"
  5. Use highest severity among merged findings
```

## Severity Calibration

### Severity Criteria

| Severity     | Impact                                        | Likelihood             | Examples                                     |
| ------------ | --------------------------------------------- | ---------------------- | -------------------------------------------- |
| **Critical** | Data loss, security breach, complete failure  | Certain or very likely | SQL injection, auth bypass, data corruption  |
| **High**     | Significant functionality impact, degradation | Likely                 | Memory leak, missing validation, broken flow |
| **Medium**   | Partial impact, workaround exists             | Possible               | N+1 query, missing edge case, unclear error  |
| **Low**      | Minimal impact, cosmetic                      | Unlikely               | Style issue, minor optimization, naming      |

### Calibration Rules

- Security vulnerabilities exploitable by external users: always Critical or High
- Performance issues in hot paths: at least Medium
- Missing tests for critical paths: at least Medium
- Accessibility violations for core functionality: at least Medium
- Code style issues with no functional impact: Low

## Consolidated Report Template

```markdown
## Code Review Report

**Target**: {files/PR/directory}
**Reviewers**: {dimension-1}, {dimension-2}, {dimension-3}
**Date**: {date}
**Files Reviewed**: {count}

### Critical Findings ({count})

#### [CR-001] {Title}

**Location**: `{file}:{line}`
**Dimension**: {Security/Performance/etc.}
**Description**: {what was found}
**Impact**: {what could happen}
**Fix**: {recommended remediation}

### High Findings ({count})

...

### Medium Findings ({count})

...

### Low Findings ({count})

...

### Summary

| Dimension    | Critical | High  | Medium | Low   | Total  |
| ------------ | -------- | ----- | ------ | ----- | ------ |
| Security     | 1        | 2     | 3      | 0     | 6      |
| Performance  | 0        | 1     | 4      | 2     | 7      |
| Architecture | 0        | 0     | 2      | 3     | 5      |
| **Total**    | **1**    | **3** | **9**  | **5** | **18** |

### Recommendation

{Overall assessment and prioritized action items}
```
