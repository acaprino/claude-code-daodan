---
name: maintain-claude-md
description: >
  Audit and improve existing CLAUDE.md with ground truth verification and guided improvements.
  TRIGGER WHEN: the user asks to audit, update, verify, or improve an existing CLAUDE.md against the current codebase.
  DO NOT TRIGGER WHEN: creating a CLAUDE.md from scratch (use /project-setup:create-claude-md).
subagent: project-setup:claude-md-auditor
---

# Maintain CLAUDE.md File

## CRITICAL RULES

1. **Keep CLAUDE.md under 40,000 characters.** This is a hard cap (Claude Code surfaces a performance warning above this threshold). Run `wc -c CLAUDE.md` after every edit. Target <35k to leave headroom. If the audit finds the file already over 40k, the **primary fix** is to extract sections to `docs/<topic>.md` and replace them with thin `Read docs/<topic>.md` pointers. Never finalize an edit that leaves the file over 40k.
2. **Verify against codebase.** Every claim in CLAUDE.md must be checked against actual files, commands, and dependencies.
3. **Show findings before changing.** Present the audit report and get approval before modifying anything.
4. **Never delete user preferences** unless the user explicitly approves. Preferences (coding style, workflow choices) are intentional.
5. **Never enter plan mode.** Execute immediately.

This command launches an interactive session to audit and optionally improve your `CLAUDE.md` file. It verifies accuracy, detects obsolete information, and guides you through prioritized improvements.

## What This Does

The agent will:
1. Analyze your codebase bottom-up (dependencies, entry points, source, config, tests, docs)
2. Read your `CLAUDE.md` last and verify every claim against established ground truth
3. Detect obsolete file paths, dependencies, or commands
4. Identify gaps - undocumented commands, dependencies, configs, or patterns
5. Check for best practices (conciseness, progressive disclosure, instruction economy)
6. Present findings with prioritized recommendations
7. Ask if you want to apply improvements
8. If yes: Guide you through interactive improvement workflow
9. If no: Provide detailed audit report only

## When to Use

- After major refactoring or restructuring
- When you suspect `CLAUDE.md` is outdated
- Periodic maintenance (quarterly recommended)
- Before onboarding new team members
- After significant dependency updates
- When Claude seems to be working from wrong assumptions
- After team discussion about what Claude should know
- After learning what works/doesn't work with Claude
- Want to modernize CLAUDE.md based on best practices

## Example Interactive Flow

### Scenario 1: Audit with Improvements

```
Agent: I've audited CLAUDE.md. Found 3 critical issues, 5 high priority, 4 medium priority.

       Critical Issues:
       1. File path src/api/ doesn't exist (actual: src/routes/api/)
       2. References webpack but project uses Vite
       3. Command "npm run build:prod" not found in package.json

       Would you like me to fix these issues?
You:   Yes

Agent: Should I fix all critical issues? (Recommended: Yes)
You:   Yes

Agent: Done. High priority issues:
       1. File is 450 lines (recommend <300)
       2. Duplicates code from README
       3. Contains style rules (should delegate to biome.json)
       4. Missing info about Vite build system
       5. Obsolete Redux docs (project uses Zustand)

       Which should I prioritize?
       A) All of them
       B) Just reduce length and remove duplicates
       C) Let me choose individually
You:   B

Agent: I can reduce from 450 to ~180 lines by:
       - Moving detailed guides to docs/development.md
       - Removing code samples (replace with file references)
       - Removing README duplicates

       I also found gaps in your CLAUDE.md:
       - "npm run lint" exists in package.json but not documented
       - Prisma ORM is a key dependency but not mentioned
       - docker-compose.yml not referenced

       I found these patterns to potentially document:
       - Custom hooks usage (src/hooks/)
       - API conventions with React Query
       - Feature-based folder structure

       Should I include these?
You:   Yes for hooks and API conventions, skip folder structure

Agent: I see both REST and GraphQL endpoints. Which should Claude prioritize?
You:   GraphQL - REST is legacy

Agent: Here's the improved version (185 lines):
       [Shows diff]
       Apply these changes?
You:   Yes

Agent: Applied! Your CLAUDE.md is now:
       - 185 lines (was 450)
       - All paths verified
       - No code duplication
       - Focuses on hooks, API conventions, GraphQL
       - References docs/development.md for details
```

### Scenario 2: Audit Only (No Changes)

```
Agent: I've audited CLAUDE.md. Found 2 critical issues, 3 high priority, 5 medium priority.

       Critical Issues:
       1. File path src/components/old/ doesn't exist
       2. Command "npm test:ci" not found in package.json

       Would you like me to fix these issues?
You:   No

Agent: Understood. Here's the complete audit report:

       ✅ Verified Claims (23 items)
       - Package manager: npm
       - Test framework: Jest
       - Build system: Vite
       ...

       ❌ Critical Issues (2)
       1. File path src/components/old/ doesn't exist
          → Actual path: src/components/legacy/
       2. Command "npm test:ci" not found
          → Available: npm test, npm run test:watch

       [HIGH] High Priority (3)
       1. File length: 380 lines (recommend <300)
       2. Duplicates content from README.md
       3. Missing documentation for new GraphQL API

       [MED] Medium Priority (5)
       ...

       Audit complete. Run /maintain-claude-md again when ready to apply fixes.
```

## Audit Verification

The agent verifies:
- **File size <40k characters**: Runs `wc -c CLAUDE.md`. Any value over 40,000 is a Critical finding (Claude Code performance warning threshold); 35,000-40,000 is High (no headroom). Primary fix: extract sections to `docs/<topic>.md` and link via `Read docs/<topic>.md` pointers
- **File paths**: Checks all referenced files and directories exist
- **Commands**: Validates npm scripts, build commands, test commands
- **Dependencies**: Confirms packages mentioned are actually installed
- **Tech stack**: Verifies frameworks, libraries, and tools referenced
- **Code patterns**: Checks that documented patterns exist in codebase
- **Architecture**: Validates architectural claims against actual structure
- **Uncertainty**: Flags claims that cannot be verified from codebase alone
- **Gaps**: Identifies undocumented commands, dependencies, configs, and patterns
- **Project structure completeness**: Verifies all significant directories and files are mapped with descriptions
- **Working Principles block**: Checks presence of the canonical `## Working Principles` section (the 4 Karpathy meta-rules); flags as High if missing or gutted and offers to insert
- **Karpathy guidelines pointer (optional)**: Always proposes (Medium) adding an external reference link to the fuller Karpathy guidelines below the Working Principles block - never inline the full text, just a pointer. User accepts or skips
- **External reference fix pattern**: For any section that bloats CLAUDE.md or duplicates other docs, proposes extracting to `docs/<topic>.md` and replacing with a thin `Read docs/<topic>.md` pointer
- **Best practices**: Assesses proportional sizing, progressive disclosure, structure detail

## Improvement Categories

### Critical (Auto-fix Recommended)
- File size over 40,000 characters (Claude Code performance warning threshold) - extract sections to `docs/<topic>.md` and replace with `Read docs/<topic>.md` pointers until the file is back under the cap
- Factually incorrect information
- Non-existent file paths
- Broken commands
- Obsolete dependencies

### High Priority (Usually Should Fix)
- Excessive length without substance (padding, duplication, pasted code snippets)
- Code duplication
- Missing important context
- Incomplete project structure map (missing file/directory descriptions)
- Missing or gutted `## Working Principles` block (insert the canonical 4 Karpathy meta-rules, preserve any coexisting project-specific principles)

### Medium Priority (Consider Based on Goals)
- Organizational improvements
- Better progressive disclosure
- Condensing verbose sections
- Adding helpful pointers
- Adding the optional external pointer to fuller Karpathy guidelines (link only, never inline the full text)
- Extracting bloated sections to `docs/<topic>.md` files referenced via `Read docs/<topic>.md` pointers - the primary fix for an oversized CLAUDE.md

### Low Priority (Nice to Have)
- Formatting consistency
- Minor wording improvements
- Additional examples

## Output

Depending on your choice:

**Audit Only:**
- Comprehensive audit report
- List of verified vs incorrect claims
- Obsolete information flagged
- Best practices assessment
- Prioritized recommendations
- Verification commands to confirm findings

**Audit + Improvements:**
- Updated `CLAUDE.md` based on your priorities
- All critical issues fixed
- User-approved improvements applied
- Diff showing what changed
- Verification commands
- Maintenance recommendations

## Tips for Best Results

1. **Start with audit**: Review findings before committing to improvements
2. **Be specific about priorities**: Tell the agent what matters most to your team
3. **Answer pattern questions**: Help agent understand preferred approaches when multiple exist
4. **Review diffs carefully**: Agent shows changes before applying
5. **Provide context**: Explain decisions so agent understands your preferences
6. **Iterate**: It's okay to try improvements and adjust
7. **Run quarterly**: Keep CLAUDE.md fresh with regular maintenance

## Related Commands

- `/create-claude-md` - Create new CLAUDE.md from scratch (interactive)
