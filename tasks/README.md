# Tasks Directory

This directory contains workflow artifacts for development tasks following the structured Claude Code workflow defined in `../AGENTS.md`.

## Structure

Each task gets its own subdirectory with workflow phase outputs:

```
tasks/
└── <task-name>/              # kebab-case task name
    ├── problem.md            # Phase 1: Problem statement
    ├── context.md            # Phase 2: Relevant files
    ├── plan.md               # Phase 3: Implementation plan
    ├── plan-review.md        # Phase 3: Plan review feedback
    ├── simplify-review.md    # Phase 5: Code simplification
    ├── code-review.md        # Phase 5: Security/bug review
    ├── verification.md       # Phase 6: Goal verification
    └── summary.md            # Phase 7: Final summary
```

## Example Task Names

- `implement-inline-game-invitations`
- `add-board-rendering-logic`
- `fix-capture-validation-bug`
- `setup-database-models`

## Usage

These directories are created automatically when using the workflow:

```
Use workflow to implement inline game invitations
```

See `../AGENTS.md` for complete workflow documentation.

## Notes

- Task directories serve as an audit trail
- Files can be used to resume interrupted workflows
- Keep task directories after completion for reference
- Add to `.gitignore` if you don't want to commit workflow artifacts
