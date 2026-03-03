# CLAUDE.md — AI Assistant Guide for IPad-work

## Repository Overview

**Repo:** `trigiulio-cpu/IPad-work`
**Project:** Without Loss — an automated economic theory paper generator.

You provide a paper and your critique. The tool reads both, checks the
logical soundness of every argument in the critique, formalises informal
claims into propositions with proofs, improves exposition, and outputs
a short (5-7 page) self-contained theory paper in LaTeX.

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
└── papers/                     # Generated .tex output
```

## Tech Stack

- **Language:** Python 3.11+
- **API:** Anthropic (claude-sonnet-4-6 default, configurable)
- **Templating:** Jinja2 for LaTeX assembly
- **PDF reading:** pdfminer.six (optional, for PDF inputs)
- **Output:** LaTeX (.tex files)
- **Linter:** ruff

## Key Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Install PDF support (if your inputs are PDFs)
pip install -e ".[pdf]"

# Generate a paper from a source paper + critique
python -m withoutloss generate --paper paper.pdf --critique my_notes.txt

# Use a specific model
python -m withoutloss generate --paper paper.pdf --critique notes.txt --model claude-opus-4-6

# Set page target and add extra instructions
python -m withoutloss generate --paper paper.tex --critique notes.txt --pages 7 --instructions "Focus on the welfare result"

# Set output filename
python -m withoutloss generate --paper paper.pdf --critique notes.txt --output my_response

# Lint
ruff check withoutloss/

# Compile generated LaTeX (requires texlive or similar)
pdflatex papers/my_response.tex
```

## How the Pipeline Works

1. **Read inputs** — Read the source paper and critique files
   (.txt, .tex, .md as plain text; .pdf via pdfminer).
2. **Body generation** — The model receives both texts and writes
   LaTeX sections/theorems/proofs that formalise the critique.
   It audits every argument for logical soundness.
3. **Metadata generation** — A second call produces abstract, keywords,
   and JEL codes from the generated body.
4. **Title generation** — A third call produces a concise title.
5. **Assembly** — Jinja2 renders the full LaTeX document from the template.

## Workflow

1. Place your source paper file somewhere accessible (PDF, .tex, or .txt).
2. Write your critique in a text file — informal is fine; the tool formalises it.
3. Run `python -m withoutloss generate --paper <paper> --critique <critique>`.
4. The output `.tex` file appears in `papers/`.
5. Compile with `pdflatex` to get a PDF.

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
5. **Never commit API keys** — `ANTHROPIC_API_KEY` must stay in environment
6. **Update this CLAUDE.md** when adding significant structure or tooling
