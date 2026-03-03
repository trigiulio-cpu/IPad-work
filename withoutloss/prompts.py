"""
System prompts and prompt-building logic for the Without Loss persona.

The persona is a frontier economic/financial theorist producing
referee-proof pure theory at the level of top-5 econ journals.
"""

SYSTEM_PROMPT = r"""You are Without Loss, a frontier economic and financial theorist.

You do not fabricate citations. You do not reference specific papers unless you
are certain they exist. When uncertain, you say so explicitly.

## Core Operating Principles

### 1. No Hallucination Rule (Strict)
- Do NOT fabricate citations.
- Do NOT invent literature references.
- Do NOT attribute results to named scholars unless completely certain.

### 2. Pure Theory Only
All outputs must contain:
- Explicit primitives
- Explicit agents
- Explicit constraints
- Explicit information structure
- Defined equilibrium concept
- Clearly stated assumptions
- Formal propositions/theorems
- Proof or proof sketch

No empirical discussion. No data suggestions. No calibration sections.
No regression ideas.

### 3. Mathematical Discipline
Every model must:
- Clearly define the environment before deriving results.
- Avoid undefined notation.
- Avoid logical jumps.
- Explicitly state where assumptions are used.
- Distinguish between: Definition, Lemma, Proposition, Theorem, Corollary.

If a proof is incomplete, state: "Proof sketch."
If existence/uniqueness is not proven, state:
"Existence not established under current assumptions."

## Intellectual Tone
- Severe
- Precise
- Minimalist
- Referee-proof
- No rhetorical inflation
- No buzzwords

Write like a theorist expecting a hostile seminar.

## Self-Audit Protocol (Internal)
Before producing output, verify:
- Are all variables defined?
- Is equilibrium defined formally?
- Are claims proven or clearly labeled as conjecture?
- Is any citation unverifiable? If yes, remove it.
- Are assumptions explicitly listed?
If any answer is no, revise before finalizing.

## Output Format
You produce LaTeX body content only (no preamble, no \begin{document}).
Use the theorem environments: assumption, definition, lemma, proposition,
theorem, corollary, remark, conjecture.
Use \section{}, \subsection{} for structure.
Use \E for expectation, \R for reals, \Prob for probability.
"""


def build_paper_prompt(config: dict) -> str:
    """Build the user-turn prompt that instructs the model to write the paper.

    Parameters
    ----------
    config : dict
        Paper configuration. Required keys:
            - topic: str
            - research_question: str
            - conjecture: str
            - model_primitives: str
        Optional keys:
            - source_paper: str  (paper being built upon)
            - microfoundation: str  (specific micro-foundation to start from)
            - policies: str  (policies to analyse)
            - additional_instructions: str
            - page_target: int (default 6)
    """
    page_target = config.get("page_target", 6)

    sections = [
        f"Write a short, self-contained theory paper in LaTeX (~{page_target} "
        f"pages of body content).",
        "",
        f"## Topic\n{config['topic']}",
        "",
        f"## Research Question\n{config['research_question']}",
        "",
        f"## Central Conjecture\n{config['conjecture']}",
        "",
        f"## Model Primitives\n{config['model_primitives']}",
    ]

    if config.get("source_paper"):
        sections += ["", f"## Source Paper\n{config['source_paper']}"]

    if config.get("microfoundation"):
        sections += ["", f"## Micro-foundation\n{config['microfoundation']}"]

    if config.get("policies"):
        sections += ["", f"## Policies to Analyse\n{config['policies']}"]

    if config.get("additional_instructions"):
        sections += [
            "",
            f"## Additional Instructions\n{config['additional_instructions']}",
        ]

    sections += [
        "",
        "## Structure Requirements",
        "The paper MUST contain, in order:",
        "1. \\section{Introduction} — state the question, the result, and why it matters. No fluff.",
        "2. \\section{Model} — full environment: primitives, agents, constraints, "
        "information, timing.",
        "3. \\section{Equilibrium} — define equilibrium formally, establish existence "
        "where possible.",
        "4. \\section{Policy Analysis} — introduce each policy instrument, derive its "
        "effect via propositions with proofs.",
        "5. \\section{Discussion} — interpret results, state limitations honestly.",
        "6. (Optional) \\appendix with longer proofs if needed.",
        "",
        "## Formatting Rules",
        "- Output ONLY the LaTeX body (sections, theorems, proofs). "
        "No preamble, no \\begin{document}.",
        "- Every proposition must have a proof or proof sketch.",
        "- Every variable must be defined before use.",
        "- Label all assumptions with the assumption environment.",
        "- Be skeptical of your own conjecture: if it is wrong, say so and prove "
        "the correct result instead.",
    ]

    return "\n".join(sections)


def build_abstract_prompt(body: str, config: dict) -> str:
    """Build a prompt that asks the model to write the abstract + metadata.

    Called after the body is generated so the abstract faithfully summarises
    the actual content.
    """
    return (
        "Given the following paper body, write:\n"
        "1. An abstract (max 150 words). Be precise and state the main result.\n"
        "2. A semicolon-separated list of keywords (3-6 keywords).\n"
        "3. JEL classification codes (2-4 codes).\n\n"
        "Return EXACTLY this JSON (no markdown fences):\n"
        '{"abstract": "...", "keywords": "...", "jel_codes": "..."}\n\n'
        f"## Paper Body\n{body}"
    )


def build_title_prompt(abstract: str, config: dict) -> str:
    """Build a prompt to generate a concise title."""
    return (
        "Given the following abstract, produce a single paper title.\n"
        "Rules:\n"
        "- Maximum 12 words.\n"
        "- No colons, no subtitles.\n"
        "- Precise and informative.\n"
        "- Return ONLY the title text, nothing else.\n\n"
        f"## Abstract\n{abstract}"
    )
