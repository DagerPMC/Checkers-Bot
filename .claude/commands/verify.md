---
name: verify
description: Verify implementation solves the problem using Code-Goal subagent. Use when user says /verify [task-name|problem]. Checks acceptance criteria and test coverage.
---

# Verify Command

Verify that an implementation matches its requirements.

## Usage
```
/verify [task-name]    # Verify task implementation
/verify [problem]      # Verify current changes against problem
```

## Process

1. **Gather Verification Context**
   If task-name provided:
   - Read `tasks/<task-name>/problem.md` for acceptance criteria
   - Run `git diff` for implementation changes
   - Find test files related to the task

   If problem description provided:
   - Use the description as acceptance criteria
   - Run `git diff` for recent changes

2. **Invoke Code-Goal Subagent**
   Use Task tool with this prompt:

   ```
   You are verifying that an implementation matches its requirements.

   ## Original Problem Statement
   {problem_statement}

   ## Acceptance Criteria
   {acceptance_criteria}

   ## Implementation Changes
   {diff_content}

   ## Test Cases
   {test_cases}

   ## Your Task
   Verify:

   1. **Problem Solved**: Does the implementation address the problem statement?
      - For each acceptance criterion, explain how it's met (or not)

   2. **Test Coverage**: Do the tests actually verify the solution?
      - Are acceptance criteria covered by tests?
      - Are edge cases tested?
      - Any missing test scenarios?

   3. **Completeness**: Is anything missing?
      - Partial implementations
      - TODO comments left behind
      - Incomplete error handling

   Output:
   - [ ] or [x] for each acceptance criterion with explanation
   - List of any gaps or concerns
   - Overall verdict: VERIFIED / NEEDS WORK
   ```

3. **Run Tests**
   If tests exist, run them and include results

4. **Present Results**
   Show verification status for each criterion

5. **Save Verification**
   If task directory exists, save to `tasks/<task-name>/verification.md`

## Example Output
```markdown
## Verification Results

### Acceptance Criteria

- [x] **User can invoke bot via inline query**
  Implemented in `bot/controllers/inline.py` with `@router.inline_query()` decorator

- [x] **Inline query returns "Start Checkers Game" option**
  Returns `InlineQueryResultArticle` with title "Start Checkers Game"

- [ ] **Accepting creates game in database**
  ISSUE: Game is created but status is not set to PENDING

### Test Coverage
- Inline query handler: Covered
- Accept callback: Covered
- Cancel callback: Missing test

### Gaps Found
1. Game status not set to PENDING on creation
2. No test for cancel callback

### Overall Verdict: NEEDS WORK

Would you like to address these gaps?
```
