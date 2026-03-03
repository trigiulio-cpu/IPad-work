# CLAUDE.md — AI Assistant Guide for IPad-work

## Repository Overview

**Repo:** `trigiulio-cpu/IPad-work`
**Project:** Without Loss — an automated economic theory paper generator.

This tool uses the Anthropic API to generate short (5-7 page), self-contained
theory papers in LaTeX at the level of top-5 economics journals. Papers are
driven by JSON config files that specify the topic, research question,
conjecture, and model primitives.

## Project Structure

```
IPad-work/
├── CLAUDE.md                   # This file
├── pyproject.toml              # Python project config, dependencies
├── .gitignore
├── withoutloss/                # Core Python package
│   ├── __init__.py
│   ├── __main__.py             # python -m withoutloss entry point
│   ├── cli.py                  # CLI argument parsing
│   ├── engine.py               # Multi-step generation pipeline
│   └── prompts.py              # System prompt + prompt builders
├── templates/
│   └── theory_paper.tex.jinja  # LaTeX Jinja2 template
├── configs/                    # Paper specification JSONs
│   └── moral_hazard_policy.json
└── papers/                     # Generated .tex output (gitignored except examples)
```

## Tech Stack

- **Language:** Python 3.11+
- **API:** Anthropic (claude-sonnet-4-6 default, configurable)
- **Templating:** Jinja2 for LaTeX assembly
- **Output:** LaTeX (.tex files)
- **Linter:** ruff

## Key Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Generate a paper from a config
python -m withoutloss generate configs/moral_hazard_policy.json

# Use a specific model
python -m withoutloss generate configs/my_paper.json --model claude-opus-4-6

# Validate config without generating
python -m withoutloss validate configs/my_paper.json

# Lint
ruff check withoutloss/

# Compile generated LaTeX (requires texlive or similar)
pdflatex papers/my_paper.tex
```

## How the Pipeline Works

1. **Body generation** — The model writes LaTeX sections/theorems/proofs
   guided by the "Without Loss" system prompt and the paper config.
2. **Metadata generation** — A second call produces abstract, keywords,
   and JEL codes from the generated body.
3. **Title generation** — A third call produces a concise title from the
   abstract.
4. **Assembly** — Jinja2 renders the full LaTeX document from the template.

## Paper Config Schema

JSON files in `configs/` must contain:

| Key                    | Required | Description                                    |
|------------------------|----------|------------------------------------------------|
| `topic`                | Yes      | Subject area of the paper                      |
| `research_question`    | Yes      | The precise question being investigated        |
| `conjecture`           | Yes      | The central claim to prove or disprove         |
| `model_primitives`     | Yes      | Agents, technology, information, timing        |
| `source_paper`         | No       | Paper being built upon                         |
| `microfoundation`      | No       | Specific micro-foundation to start from        |
| `policies`             | No       | Policy instruments to analyse                  |
| `additional_instructions` | No    | Extra guidance for the model                   |
| `page_target`          | No       | Target page count (default: 6)                 |

## The "Without Loss" Persona

The system prompt encodes a persona with these rules:

- **No fabricated citations** — never invent references
- **Pure theory only** — no empirics, no calibration, no data
- **Mathematical discipline** — defined environments, explicit assumptions,
  formal proofs
- **Severe, minimalist tone** — write like a theorist expecting a hostile seminar
- **Self-audit** — verify all variables defined, equilibrium formal,
  claims proven or labeled conjecture

## Development Workflow

### Branching

- **Feature branches:** `claude/<description>-<id>` or `feature/<name>`
- Write clear commit messages describing *why*

### Code Quality

- Run `ruff check withoutloss/` before committing
- Keep the package minimal — no unnecessary abstractions
- All prompt text lives in `prompts.py`; engine logic in `engine.py`

## Conventions for AI Assistants

1. **Read before writing** — understand existing code before modifying
2. **Minimal changes** — only what is necessary
3. **No speculative features** — implement what is asked
4. **Prompts are content** — treat `prompts.py` as carefully as model code;
   small wording changes can significantly affect output quality
5. **Config files are user-facing** — keep the JSON schema stable; add
   optional keys rather than changing required ones
6. **Never commit API keys** — `ANTHROPIC_API_KEY` must stay in environment
7. **Update this CLAUDE.md** when adding significant structure or tooling
