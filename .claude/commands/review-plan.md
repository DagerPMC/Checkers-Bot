---
name: review-plan
description: Review implementation plan using Plan-Reviewer subagent. Use when user says /review-plan [plan.md]. Reviews for correctness, completeness, architecture, simplicity.
---

# Review-Plan Command

Review an implementation plan from an architecture standpoint.

## Usage
```
/review-plan [path/to/plan.md]
/review-plan [task-name]
```

If task-name is provided, reads from `tasks/<task-name>/plan.md`

## Process

1. **Read the Plan**
   - Load plan content from specified file or task directory

2. **Gather Context**
   - Read problem statement if exists (`tasks/<task-name>/problem.md`)
   - Read context file if exists (`tasks/<task-name>/context.md`)

3. **Invoke Plan-Reviewer Subagent**
   Use Task tool with model: opus and this prompt:

   ```
   You are a senior software architect reviewing an implementation plan for a Checkers Telegram Bot.

   ## Problem Statement
   {problem_statement}

   ## Proposed Plan
   {plan_content}

   ## Codebase Context
   {context_summary}

   ## Project Standards
   - aiogram 3.x async patterns
   - SQLAlchemy async sessions
   - Callback data < 64 bytes
   - PEP8, 80 char lines, type hints
   - No unnecessary comments

   ## Your Task
   Review this plan critically for:

   1. **Correctness**: Does this plan actually solve the problem?
   2. **Completeness**: Are all edge cases handled?
   3. **Architecture**: Does it fit well with existing patterns?
   4. **Simplicity**: Is this the simplest solution? Can anything be removed?
   5. **Risks**: What could go wrong? Missing error handling?
   6. **Testing**: Is the test strategy adequate?
   7. **Code Standards**: Does it follow project conventions?

   For each issue found, provide:
   - Severity (Critical/Major/Minor)
   - Description of the issue
   - Suggested fix

   If the plan is acceptable, state "PLAN APPROVED" at the end.
   ```

4. **Save Review**
   - Save to `tasks/<task-name>/plan-review.md`

5. **Report Results**
   - Present review findings to user
   - If issues found, suggest revisions
   - If approved, confirm plan is ready for implementation
