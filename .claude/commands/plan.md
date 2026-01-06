---
name: plan
description: Create implementation plan using Planner subagent. Use when user says /plan [task]. Creates detailed step-by-step implementation plan.
---

# Plan Command

Create a detailed implementation plan for a task.

## Usage
```
/plan [task description]
```

## Process

1. **Gather Context**
   - Use Explore subagent to find relevant files (10-20 files)
   - Read core files to understand patterns

2. **Create Task Directory**
   - Derive task name from description (kebab-case)
   - Create `tasks/<task-name>/`

3. **Invoke Planner Subagent**
   Use Task tool with model: opus and this prompt:

   ```
   You are a senior software architect creating an implementation plan for a Checkers Telegram Bot.

   ## Problem Statement
   {task_description}

   ## Codebase Context
   ### Relevant Files:
   {relevant_files_list}

   ### File Contents:
   {file_contents}

   ## Project Standards (from CLAUDE.md)
   - Python 3.13, aiogram 3.x, async/await patterns
   - 80 char lines, PEP8, type hints
   - PostgreSQL with SQLAlchemy async
   - Follow existing middleware patterns
   - Quality checks: isort, flake8, mypy

   ## Your Task
   Create a detailed, step-by-step implementation plan that:
   1. Follows existing patterns and conventions in the codebase
   2. Minimizes changes while fully solving the problem
   3. Considers edge cases and error handling
   4. Includes specific code locations and changes
   5. Defines clear testing strategy
   6. Adheres to project code style standards

   Output a complete plan in markdown format.
   ```

4. **Save Plan**
   - Save to `tasks/<task-name>/plan.md`

## Plan Format
```markdown
## Implementation Plan: [Task Name]

### Overview
[Brief description]

### Prerequisites
- [Any setup needed]

### Implementation Steps

#### Step 1: [Step Title]
**Files:** `path/to/file.py`
**Changes:**
- [Specific change 1]
- [Specific change 2]

**Code:**
```python
# Example code snippet
```

### Testing Strategy
- [ ] [Test case 1]
- [ ] [Test case 2]

### Edge Cases Considered
- [Edge case and handling]

### Risks and Mitigations
- **Risk:** [Risk description]
  **Mitigation:** [How to address]
```
