---
name: gather-context
description: Find 10-20 relevant files for a topic. Use when user says /gather-context [topic]. Explores codebase and identifies core files, related files, and patterns.
---

# Gather-Context Command

Find and document relevant files for a topic or task.

## Usage
```
/gather-context [topic or task description]
```

## Process

1. **Use Explore Subagent**
   Use Task tool with subagent_type: Explore and thoroughness: "very thorough"

   Prompt: "Find all files relevant to: {topic}. Look for:
   - Direct implementations
   - Related functionality
   - Test files
   - Configuration files
   - Dependencies"

2. **Categorize Files**
   Group found files into:
   - **Core Files**: Directly involved in the topic
   - **Related Files**: May be affected or reference
   - **Test Files**: Existing tests to consider
   - **Config Files**: Relevant configuration

3. **Read Key Files**
   Read the most important files to identify:
   - Existing patterns and conventions
   - Code style used
   - Architecture decisions

4. **Document Patterns**
   Note any patterns observed:
   - Router patterns
   - Middleware usage
   - Database access patterns
   - Error handling patterns

5. **Create Output**
   If a task directory exists, save to `tasks/<task-name>/context.md`
   Otherwise, present directly to user

## Output Format
```markdown
## Relevant Files

### Core Files (directly involved):
1. `path/to/file1.py` - [Brief description of relevance]
2. `path/to/file2.py` - [Brief description of relevance]

### Related Files (may be affected):
1. `path/to/related1.py` - [Brief description]

### Test Files:
1. `path/to/test_file.py` - [Existing tests to consider]

### Config Files:
1. `path/to/config.py` - [Relevant settings]

### Key Patterns Observed:
- [Pattern 1: description]
- [Pattern 2: description]

### Dependencies:
- [External package 1]
- [Internal module 1]
```
