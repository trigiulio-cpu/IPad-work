# CLAUDE.md — AI Assistant Guide for IPad-work

## Repository Overview

**Repo:** `trigiulio-cpu/IPad-work`
**Status:** Greenfield project — this repository is in its initial setup phase.

This is a new repository. As the project grows, this file should be updated to reflect the evolving codebase structure, tooling, and conventions.

## Project Structure

```
IPad-work/
├── CLAUDE.md          # This file — AI assistant guide
└── (project files)    # To be added as the project develops
```

## Development Workflow

### Branching

- **Default branch:** `main` (to be created with the initial commit)
- **Feature branches:** Use descriptive names prefixed by category (e.g., `feature/`, `fix/`, `docs/`)
- Claude-generated branches follow the pattern: `claude/<description>-<id>`

### Commits

- Write clear, concise commit messages describing *why* a change was made
- Keep commits focused — one logical change per commit
- Do not amend published commits; create new commits instead

### Code Quality

- Prefer simple, readable code over clever abstractions
- Do not over-engineer — solve the problem at hand without speculative features
- Follow the conventions of whatever language/framework is adopted in this project

## Conventions for AI Assistants

### General Rules

1. **Read before writing** — Always read existing files before proposing changes
2. **Minimal changes** — Only modify what is necessary to complete the task
3. **No unnecessary files** — Do not create files unless required; prefer editing existing ones
4. **No speculative features** — Implement what is asked, nothing more
5. **Security first** — Never introduce secrets, credentials, or known vulnerabilities into code

### When Working in This Repo

- Check for existing configuration files (package.json, Makefile, pyproject.toml, etc.) before assuming the tech stack
- Run existing tests and linters when available before and after making changes
- Respect `.gitignore` — do not commit generated files, build artifacts, or secrets
- Update this CLAUDE.md when you add significant tooling, structure, or conventions

### Things to Avoid

- Do not add comments, docstrings, or type annotations to code you did not change
- Do not refactor surrounding code when fixing a bug
- Do not add error handling for impossible scenarios
- Do not create abstractions for one-time operations
- Do not use emojis unless the user requests them
