---
name: review-code
description: Review code for bugs and vulnerabilities using Code-Reviewer subagent. Use when user says /review-code [file|staged]. Finds security issues, bugs, performance problems.
---

# Review-Code Command

Find bugs, security vulnerabilities, and performance issues in code.

## Usage
```
/review-code [file]       # Review specific file
/review-code staged       # Review staged changes
/review-code [task-name]  # Review changes from task
```

## Process

1. **Get Code to Review**
   - If file: Read the file content
   - If staged: Run `git diff --cached`
   - If task-name: Run `git diff` on task-related files

2. **Get Original Context**
   - Read original files for full context if reviewing diff

3. **Invoke Code-Reviewer Subagent**
   Use Task tool with model: opus and this prompt:

   ```
   You are a security-focused code reviewer for a Telegram bot application.

   ## Changes to Review
   {diff_content}

   ## Original Files Context
   {original_files}

   ## Your Task
   Review the code for:

   1. **Security Vulnerabilities**
      - SQL injection, command injection
      - Exposed secrets or sensitive data
      - Insecure deserialization
      - Telegram API misuse
      - Callback data validation

   2. **Bugs**
      - Null/None references
      - Off-by-one errors
      - Race conditions (async issues)
      - Incorrect error handling
      - Logic errors in game rules

   3. **Performance Issues**
      - N+1 queries
      - Memory leaks
      - Blocking operations in async code
      - Inefficient algorithms

   4. **Breaking Changes**
      - API compatibility issues
      - Database migration risks

   For each issue:
   - Severity (Critical/High/Medium/Low)
   - Location (file:line)
   - Description
   - Suggested fix
   - Impact if not fixed

   If no issues found, state "NO ISSUES FOUND".
   ```

4. **Present Findings**
   Group by severity (Critical first)

5. **Apply Fixes**
   For each issue, offer to apply the suggested fix

6. **Save Review**
   If task directory exists, save to `tasks/<task-name>/code-review.md`

## Example Output
```markdown
## Code Review Results

### Critical Issues

#### 1. SQL Injection Vulnerability
**Location:** `bot/db/queries.py:23`
**Description:** User input directly interpolated into SQL query
**Impact:** Attacker could read/modify database

**Current:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**Fix:**
```python
query = select(User).where(User.id == user_id)
```

---

### High Issues
[...]

### Medium Issues
[...]

### Summary
- Critical: 1
- High: 2
- Medium: 3
- Low: 1

Fix critical issues? [y/n]
```
