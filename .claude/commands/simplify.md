---
name: simplify
description: Simplify code using Code-Simplifier subagent. Use when user says /simplify [file|staged]. Removes unnecessary complexity, dead code, redundant abstractions.
---

# Simplify Command

Remove unnecessary complexity and improve code quality.

## Usage
```
/simplify [file]       # Simplify specific file
/simplify staged       # Simplify staged changes
/simplify [task-name]  # Simplify changes from task
```

## Process

1. **Get Code to Review**
   - If file: Read the file content
   - If staged: Run `git diff --cached`
   - If task-name: Run `git diff` on task-related files

2. **Invoke Code-Simplifier Subagent**
   Use Task tool with this prompt:

   ```
   You are a code simplification expert for Python/aiogram applications.

   ## Changes to Review
   {diff_or_file_content}

   ## Project Standards
   - Python 3.13 with type hints
   - Self-documenting code - avoid unnecessary comments
   - Async/await patterns throughout
   - PEP8, 80 char lines

   ## Your Task
   Analyze the code for:

   1. **Redundant code**: Duplicate logic that can be consolidated
   2. **Dead code**: Unused variables, unreachable branches
   3. **Unnecessary abstraction**: Over-engineering, premature generalization
   4. **Missed abstractions**: Repeated patterns that should be functions
   5. **Verbose constructs**: Code that can be simplified using Python idioms
   6. **Redundant checks**: Conditions that are always true/false
   7. **Unnecessary comments**: Comments that don't add value

   For each finding:
   - Location (file:line)
   - Issue description
   - Suggested simplification with code example

   Focus only on the changed code. Don't suggest changes to unmodified code.
   ```

3. **Present Findings**
   Show each issue with before/after code examples

4. **Apply Fixes**
   If user approves, apply the suggested simplifications

5. **Save Review**
   If task directory exists, save to `tasks/<task-name>/simplify-review.md`

## Example Output
```markdown
## Simplification Suggestions

### Issue 1: Redundant null check
**Location:** `bot/controllers/game.py:45`
**Issue:** Checking for None after already validated by Pydantic

**Before:**
```python
if user_id is not None:
    user = await get_user(user_id)
```

**After:**
```python
user = await get_user(user_id)
```

---

Found 3 simplification opportunities. Apply changes? [y/n]
```
