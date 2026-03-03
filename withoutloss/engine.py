"""
Core generation engine.

Orchestrates multi-step paper generation:
  1. Generate the paper body (sections, proofs, theorems).
  2. Generate abstract + metadata from the body.
  3. Generate title from the abstract.
  4. Assemble into a compilable LaTeX document via Jinja template.
"""

import json
import os
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .prompts import (
    SYSTEM_PROMPT,
    build_abstract_prompt,
    build_paper_prompt,
    build_title_prompt,
)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "claude-sonnet-4-6"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "papers"


def _call_api(
    system: str,
    user: str,
    *,
    model: str | None = None,
    max_tokens: int = 12000,
    temperature: float = 0.3,
) -> str:
    """Call the Anthropic messages API and return the text response.

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

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def _parse_json_response(text: str) -> dict:
    """Robustly parse a JSON object from the model response."""
    # Try direct parse first
    text = text.strip()
    # Strip markdown fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


# ---------------------------------------------------------------------------
# Pipeline steps
# ---------------------------------------------------------------------------


def generate_body(config: dict, *, model: str | None = None) -> str:
    """Step 1: Generate the paper body (sections + proofs)."""
    prompt = build_paper_prompt(config)
    print("[1/4] Generating paper body...")
    body = _call_api(SYSTEM_PROMPT, prompt, model=model, max_tokens=12000)
    return body


def generate_metadata(
    body: str, config: dict, *, model: str | None = None
) -> dict:
    """Step 2: Generate abstract, keywords, JEL codes from the body."""
    prompt = build_abstract_prompt(body, config)
    print("[2/4] Generating abstract and metadata...")
    raw = _call_api(SYSTEM_PROMPT, prompt, model=model, max_tokens=1000)
    return _parse_json_response(raw)


def generate_title(
    abstract: str, config: dict, *, model: str | None = None
) -> str:
    """Step 3: Generate the paper title."""
    prompt = build_title_prompt(abstract, config)
    print("[3/4] Generating title...")
    title = _call_api(
        SYSTEM_PROMPT, prompt, model=model, max_tokens=100, temperature=0.2
    )
    return title.strip().strip('"').strip("'")


def assemble_latex(
    title: str,
    abstract: str,
    keywords: str,
    jel_codes: str,
    body: str,
    *,
    author: str = "Without Loss",
    appendix: str = "",
    template_name: str = "theory_paper.tex.jinja",
) -> str:
    """Step 4: Render the full LaTeX document from the Jinja template."""
    print("[4/4] Assembling LaTeX document...")
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        # Keep LaTeX braces from being interpreted
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
    )


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------


def generate_paper(
    config: dict,
    *,
    model: str | None = None,
    output_name: str | None = None,
) -> Path:
    """Run the full paper-generation pipeline.

    Parameters
    ----------
    config : dict
        Paper specification (see prompts.build_paper_prompt for schema).
    model : str, optional
        Anthropic model ID to use.
    output_name : str, optional
        Base name for the output .tex file (without extension).

    Returns
    -------
    Path
        Path to the generated .tex file.
    """
    # Step 1: body
    body = generate_body(config, model=model)

    # Step 2: metadata
    meta = generate_metadata(body, config, model=model)
    abstract = meta["abstract"]
    keywords = meta.get("keywords", "")
    jel_codes = meta.get("jel_codes", "")

    # Step 3: title
    title = generate_title(abstract, config, model=model)

    # Step 4: assemble
    latex = assemble_latex(
        title=title,
        abstract=abstract,
        keywords=keywords,
        jel_codes=jel_codes,
        body=body,
    )

    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = output_name or _slugify(title)
    out_path = OUTPUT_DIR / f"{fname}.tex"
    out_path.write_text(latex, encoding="utf-8")
    print(f"\nPaper written to: {out_path}")
    return out_path


def _slugify(text: str) -> str:
    """Convert title to a filesystem-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:60]
