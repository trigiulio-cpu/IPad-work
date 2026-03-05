"""
Core generation engine.

Orchestrates multi-step paper generation from a source paper + critique:
  1. Generate the paper body (sections, proofs, theorems).
  2. Generate abstract + metadata from the body.
  3. Generate title from the abstract.
  4. Assemble into a compilable LaTeX document via Jinja template.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .prompts import (
    SYSTEM_PROMPT,
    build_abstract_prompt,
    build_critique_paper_prompt,
    build_title_prompt,
)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "claude-sonnet-4-6"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "papers"

MAX_RETRIES = 5
RETRY_BACKOFF = 2  # exponential back-off base (seconds)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_fences(text: str) -> str:
    """Strip markdown code fences from model output."""
    text = text.strip()
    text = re.sub(r"^```(?:latex|tex|json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _call_api(
    system: str,
    user: str,
    *,
    model: str | None = None,
    max_tokens: int = 12000,
    temperature: float = 0.3,
) -> str:
    """Call the Anthropic messages API and return the text response.

    Retries transient errors with exponential backoff.
    Requires ANTHROPIC_API_KEY in the environment.
    """
    try:
        import anthropic
    except ImportError as exc:
        raise RuntimeError(
            "The 'anthropic' package is required. Install with: "
            "pip install anthropic"
        ) from exc

    client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY from env
    model = model or os.getenv("WITHOUTLOSS_MODEL", DEFAULT_MODEL)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text
        except Exception as exc:
            # Don't retry auth errors or invalid requests
            exc_str = str(exc)
            if "401" in exc_str or "authentication" in exc_str.lower():
                raise
            if attempt == MAX_RETRIES - 1:
                raise
            wait = min(RETRY_BACKOFF ** (attempt + 1), 60)
            print(f"  [retry {attempt + 1}/{MAX_RETRIES}] {exc} — waiting {wait}s")
            time.sleep(wait)

    # Should not reach here, but satisfy type checker
    raise RuntimeError("API call failed after all retries")


def _parse_json_response(text: str) -> dict:
    """Robustly parse a JSON object from the model response."""
    text = _strip_fences(text)
    # Try to find a JSON object if there's extra text around it
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return json.loads(text)


def read_input_file(path: Path) -> str:
    """Read a paper or critique file.

    Supports .txt, .tex, and .md files as plain text.
    For .pdf files, attempts extraction via pdfminer.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if path.suffix.lower() == ".pdf":
        try:
            from pdfminer.high_level import extract_text

            return extract_text(str(path))
        except ImportError as exc:
            raise RuntimeError(
                "Reading PDFs requires pdfminer.six. Install with: "
                "pip install pdfminer.six"
            ) from exc

    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------


def generate_body(
    paper_text: str,
    critique_text: str,
    *,
    model: str | None = None,
    page_target: int = 6,
    additional_instructions: str = "",
) -> str:
    """Step 1: Generate the paper body from paper + critique."""
    prompt = build_critique_paper_prompt(
        paper_text,
        critique_text,
        page_target=page_target,
        additional_instructions=additional_instructions,
    )
    print("[1/4] Generating paper body from critique...")
    body = _call_api(SYSTEM_PROMPT, prompt, model=model, max_tokens=12000)
    return _strip_fences(body)


def generate_metadata(body: str, *, model: str | None = None) -> dict:
    """Step 2: Generate abstract, keywords, JEL codes from the body."""
    prompt = build_abstract_prompt(body)
    print("[2/4] Generating abstract and metadata...")
    raw = _call_api(SYSTEM_PROMPT, prompt, model=model, max_tokens=1000)
    meta = _parse_json_response(raw)

    # Validate required fields with fallbacks
    if "abstract" not in meta:
        print("  Warning: model did not return 'abstract' key, using empty string")
        meta["abstract"] = ""
    if "keywords" not in meta:
        meta["keywords"] = ""
    if "jel_codes" not in meta:
        meta["jel_codes"] = ""

    return meta


def generate_title(abstract: str, *, model: str | None = None) -> str:
    """Step 3: Generate the paper title."""
    prompt = build_title_prompt(abstract)
    print("[3/4] Generating title...")
    title = _call_api(
        SYSTEM_PROMPT, prompt, model=model, max_tokens=100, temperature=0.2
    )
    return _strip_fences(title).strip('"').strip("'")


def assemble_latex(
    title: str,
    abstract: str,
    keywords: str,
    jel_codes: str,
    body: str,
    *,
    author: str = "Without Loss",
    appendix: str = "",
    bibliography: str = "",
    template_name: str = "theory_paper.tex.jinja",
) -> str:
    """Step 4: Render the full LaTeX document from the Jinja template."""
    print("[4/4] Assembling LaTeX document...")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="{{",
        variable_end_string="}}",
        comment_start_string="<#",
        comment_end_string="#>",
    )
    template = env.get_template(template_name)
    return template.render(
        title=title,
        author=author,
        abstract=abstract,
        keywords=keywords,
        jel_codes=jel_codes,
        body=body,
        appendix=appendix,
        bibliography=bibliography,
    )


def compile_latex(tex_path: Path) -> Path | None:
    """Compile a .tex file to PDF using pdflatex + bibtex if available.

    Returns the path to the PDF on success, or None on failure.
    """
    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        print("  Warning: pdflatex not found, skipping compilation")
        return None

    tex_dir = tex_path.parent
    tex_name = tex_path.stem

    def run_pdflatex():
        return subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            timeout=120,
        )

    try:
        # First pass
        result = run_pdflatex()
        if result.returncode != 0:
            print(f"  pdflatex failed (pass 1). See {tex_name}.log for details.")
            return None

        # Run bibtex if a .bib file exists alongside the .tex
        bib_path = tex_dir / f"{tex_name}.bib"
        bibtex = shutil.which("bibtex")
        if bib_path.exists() and bibtex:
            subprocess.run(
                [bibtex, tex_name],
                cwd=tex_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Two more passes for references
            run_pdflatex()
            run_pdflatex()
        else:
            # Second pass for cross-references
            run_pdflatex()

        pdf_path = tex_dir / f"{tex_name}.pdf"
        if pdf_path.exists():
            return pdf_path
        print(f"  PDF not produced. See {tex_name}.log for details.")
        return None

    except subprocess.TimeoutExpired:
        print("  pdflatex timed out")
        return None


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------


def generate_paper(
    paper_path: Path,
    critique_path: Path,
    *,
    model: str | None = None,
    output_name: str | None = None,
    page_target: int = 6,
    additional_instructions: str = "",
    bib_path: Path | None = None,
    compile: bool = False,
) -> Path:
    """Run the full paper-generation pipeline.

    Parameters
    ----------
    paper_path : Path
        Path to the original paper file (.txt, .tex, .md, or .pdf).
    critique_path : Path
        Path to the critique file (.txt, .tex, .md, or .pdf).
    model : str, optional
        Anthropic model ID to use.
    output_name : str, optional
        Base name for the output .tex file (without extension).
    page_target : int
        Target page count for the output.
    additional_instructions : str
        Extra guidance for the model.
    bib_path : Path, optional
        Path to a .bib file to include in the document.
    compile : bool
        If True, compile the .tex file to PDF after generation.

    Returns
    -------
    Path
        Path to the generated .tex file (or .pdf if compile=True and
        compilation succeeds).
    """
    # Read inputs
    print(f"Reading paper: {paper_path}")
    paper_text = read_input_file(paper_path)
    print(f"Reading critique: {critique_path}")
    critique_text = read_input_file(critique_path)

    # Step 1: body
    body = generate_body(
        paper_text,
        critique_text,
        model=model,
        page_target=page_target,
        additional_instructions=additional_instructions,
    )

    # Step 2: metadata
    meta = generate_metadata(body, model=model)
    abstract = meta["abstract"]
    keywords = meta.get("keywords", "")
    jel_codes = meta.get("jel_codes", "")

    # Step 3: title
    title = generate_title(abstract, model=model)

    # Determine output name
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = output_name or _slugify(title)

    # Handle bibliography
    bibliography = ""
    if bib_path:
        bib_path = Path(bib_path)
        if not bib_path.exists():
            print(f"  Warning: .bib file not found: {bib_path}")
        else:
            # Copy .bib file next to the output .tex
            dest_bib = OUTPUT_DIR / f"{fname}.bib"
            shutil.copy2(bib_path, dest_bib)
            bibliography = fname  # just the base name, no extension

    # Step 4: assemble
    latex = assemble_latex(
        title=title,
        abstract=abstract,
        keywords=keywords,
        jel_codes=jel_codes,
        body=body,
        bibliography=bibliography,
    )

    # Write output
    out_path = OUTPUT_DIR / f"{fname}.tex"
    out_path.write_text(latex, encoding="utf-8")
    print(f"\nPaper written to: {out_path}")

    # Optional compilation
    if compile:
        print("Compiling LaTeX to PDF...")
        pdf_path = compile_latex(out_path)
        if pdf_path:
            print(f"PDF written to: {pdf_path}")
            return pdf_path

    return out_path


def _slugify(text: str) -> str:
    """Convert title to a filesystem-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:60]
