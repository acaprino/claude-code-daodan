---
name: parallel-debugging
description: >
  Debug complex issues using competing hypotheses with parallel investigation,
  evidence collection, and root cause arbitration. Use this skill when debugging
  bugs with multiple potential causes, performing root cause analysis, or
  organizing parallel investigation workflows.
version: 1.2.0
---

# Parallel Debugging

Framework for debugging complex issues using the Analysis of Competing Hypotheses (ACH) methodology with parallel agent investigation.

## When to Use This Skill

- Bug has multiple plausible root causes
- Initial debugging attempts haven't identified the issue
- Issue spans multiple modules or components
- Need systematic root cause analysis with evidence
- Want to avoid confirmation bias in debugging

## Hypothesis Generation Framework

Generate hypotheses across 6 failure mode categories:

### 1. Logic Error

- Incorrect conditional logic (wrong operator, missing case)
- Off-by-one errors in loops or array access
- Missing edge case handling
- Incorrect algorithm implementation

### 2. Data Issue

- Invalid or unexpected input data
- Type mismatch or coercion error
- Null/undefined/None where value expected
- Encoding or serialization problem
- Data truncation or overflow

### 3. State Problem

- Race condition between concurrent operations
- Stale cache returning outdated data
- Incorrect initialization or default values
- Unintended mutation of shared state
- State machine transition error

### 4. Integration Failure

- API contract violation (request/response mismatch)
- Version incompatibility between components
- Configuration mismatch between environments
- Missing or incorrect environment variables
- Network timeout or connection failure

### 5. Resource Issue

- Memory leak causing gradual degradation
- Connection pool exhaustion
- File descriptor or handle leak
- Disk space or quota exceeded
- CPU saturation from inefficient processing

### 6. Environment

- Missing runtime dependency
- Wrong library or framework version
- Platform-specific behavior difference
- Permission or access control issue
- Timezone or locale-related behavior

## Evidence Collection Standards

### What Constitutes Evidence

| Evidence Type     | Strength | Example                                                         |
| ----------------- | -------- | --------------------------------------------------------------- |
| **Direct**        | Strong   | Code at `file.ts:42` shows `if (x > 0)` should be `if (x >= 0)` |
| **Correlational** | Medium   | Error rate increased after commit `abc123`                      |
| **Testimonial**   | Weak     | "It works on my machine"                                        |
| **Absence**       | Variable | No null check found in the code path                            |

### Citation Format

Always cite evidence with file:line references:

```
**Evidence**: The validation function at `src/validators/user.ts:87`
does not check for empty strings, only null/undefined. This allows
empty email addresses to pass validation.
```

### Confidence Levels

| Level               | Criteria                                                                            |
| ------------------- | ----------------------------------------------------------------------------------- |
| **High (>80%)**     | Multiple direct evidence pieces, clear causal chain, no contradicting evidence      |
| **Medium (50-80%)** | Some direct evidence, plausible causal chain, minor ambiguities                     |
| **Low (<50%)**      | Mostly correlational evidence, incomplete causal chain, some contradicting evidence |

## Result Arbitration Protocol

After all investigators report:

### Step 1: Categorize Results

- **Confirmed**: High confidence, strong evidence, clear causal chain
- **Plausible**: Medium confidence, some evidence, reasonable causal chain
- **Falsified**: Evidence contradicts the hypothesis
- **Inconclusive**: Insufficient evidence to confirm or falsify

### Step 2: Compare Confirmed Hypotheses

If multiple hypotheses are confirmed, rank by:

1. Confidence level
2. Number of supporting evidence pieces
3. Strength of causal chain
4. Absence of contradicting evidence

### Step 3: Determine Root Cause

- If one hypothesis clearly dominates: declare as root cause
- If multiple hypotheses are equally likely: may be compound issue (multiple contributing causes)
- If no hypotheses confirmed: generate new hypotheses based on evidence gathered

### Step 4: Validate Fix

Before declaring the bug fixed:

- [ ] Fix addresses the identified root cause
- [ ] Fix doesn't introduce new issues
- [ ] Original reproduction case no longer fails
- [ ] Related edge cases are covered
- [ ] Relevant tests are added or updated

## Runtime Evidence Pattern

When arbitration leaves hypotheses Plausible or Inconclusive and static evidence is exhausted, inject targeted runtime logs to disambiguate. The pattern is designed so cleanup is mechanical (grep + delete) and the logs never leak into production.

### Log Convention

Every injected log MUST follow this format:

```
[DEBUG] [{file}:{line}] {short description} { {relevant vars} }
```

Concrete examples per language:

```javascript
// JS/TS
console.log("[DEBUG] [auth.ts:42] before token verify", { tokenLen: token.length, hasUser: !!user })
```

```python
# Python
print(f"[DEBUG] [auth.py:42] before token verify", {"token_len": len(token), "has_user": user is not None})
# or
logger.debug("[DEBUG] [auth.py:42] before token verify token_len=%d has_user=%s", len(token), user is not None)
```

```rust
// Rust
eprintln!("[DEBUG] [auth.rs:42] before token verify token_len={} has_user={}", token.len(), user.is_some());
```

```go
// Go
fmt.Fprintf(os.Stderr, "[DEBUG] [auth.go:42] before token verify token_len=%d has_user=%v\n", len(token), user != nil)
```

The `[DEBUG]` prefix is non-negotiable. It is the cleanup anchor.

### Strategic Placement

Pick 3-5 points, not more. Flooding logs makes signal harder to extract.

| Location          | Captures                            |
| ----------------- | ----------------------------------- |
| Function entry    | Confirms execution path, args       |
| Before async call | State just before the operation     |
| After async call  | Result, error, timing               |
| Conditional       | Which branch was taken              |
| Catch block       | Error name, message, partial state  |

### What NOT to Log

- Passwords, tokens, API keys (use length or `present/absent` markers instead)
- PII (email, phone, names) unless masked
- Full request/response bodies (use sizes and selected fields)
- Inside hot loops without rate limiting

### Cleanup Protocol

After the bug is verified fixed, remove every `[DEBUG]` log. The grep is the source of truth — if grep returns zero matches, cleanup is complete.

```bash
# JS/TS
grep -rn '\[DEBUG\]' . --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx'

# Python
grep -rn '\[DEBUG\]' . --include='*.py'

# Rust
grep -rn '\[DEBUG\]' . --include='*.rs'

# Go
grep -rn '\[DEBUG\]' . --include='*.go'
```

Multi-line console statements that span more than the matched line must be removed in full. Verify the file still parses after deletion.

### Iteration Cap

A debug session should perform at most **2 rounds** of log injection. If after the second round the hypotheses are still Inconclusive, escalate to the user with a written summary of what has been ruled out and what additional context (MCP access, production logs, a minimal reproduction) would be needed.

## Specialized Investigation Agents

When a hypothesis falls into one of the 6 failure mode categories above, prefer a specialized investigator over a generic `team-debugger`. The specialized agent loads the right knowledge base automatically and produces higher-precision findings.

| Failure mode category | Preferred specialized agent | Notes |
|---|---|---|
| Logic Error | `senior-review:code-auditor` | Failure-flow tracing + pattern consistency |
| Data Issue | `senior-review:code-auditor` or `senior-review:security-auditor` | The latter when the data crosses a trust boundary |
| State Problem (concurrency, cache, mutation) | `senior-review:ui-race-auditor` for UI; `senior-review:distributed-flow-auditor` for cross-service | |
| Integration Failure | `senior-review:distributed-flow-auditor` | Both sides of the contract |
| Resource Issue | `senior-review:code-auditor` + `react-development:react-performance-optimizer` (if frontend) | |
| Environment | `senior-review:chicken-egg-detector` | Startup cycles, init order, config bootstrap |

`team-debugger` remains the fallback when no specialized agent matches the hypothesis cleanly, or when the investigation is too cross-cutting for a single specialist.

## Sub-spawning caveat

When a `team-debugger` spawns a specialized sub-agent via the `Agent` tool (e.g. to deepen one of the 6 categories), that sub-agent itself **cannot** spawn further sub-agents (Claude Agent SDK restriction: one-level subagent nesting). If a hypothesis requires deeper delegation, the debugger reports this to the team lead rather than chaining indirectly; the lead has the team-level view to decide whether to re-spawn at the top level or escalate to the user.

## Output Persistence

The `team-debugger` agent and the specialized investigators all accept a spawner-provided output file path. When the orchestrator spawns an investigator and wants the structured report on disk (the default in `/team-review` and similar pipelines), the spawn prompt must include `Write your final report to <path>`. Investigators write directly with the `Write` tool rather than returning the report only as message text.

Reference: `docs/references/agent-teams-best-practices.md` § Operational do's and don'ts.
