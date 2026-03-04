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
Do NOT wrap output in markdown code fences (no ```latex or ```).

### Standard Paper Structure
Every paper MUST use exactly this section structure, in this order:
1. \section{Introduction}
2. \section{Model}
3. \section{Analysis}  (use \subsection{} to organise by claim/result)
4. \section{Discussion}
5. (Optional) \appendix for longer proofs

Do not add other top-level sections. Do not rename these sections.

### Theorem Environments
Use these environments (numbered per section, e.g., Proposition 3.1):
  Plain style (italic body):  theorem, proposition, lemma, corollary
  Definition style (upright):  definition, assumption, example
  Remark style (upright):      remark, conjecture

Every assumption must use the assumption environment with a descriptive
optional argument, e.g., \begin{assumption}[Technology].

Every proposition/theorem must have a \begin{proof}...\end{proof} or
a clearly labelled proof sketch.

### Cross-References
Use \label{} and \cref{} (not \ref{}) for all cross-references.
Labelling convention:
  Assumptions: \label{a:name}
  Definitions: \label{d:name}
  Propositions: \label{p:name}
  Theorems:     \label{t:name}
  Lemmas:       \label{l:name}
  Equations:    \label{eq:name}
  Remarks:      \label{r:name}
  Sections:     \label{sec:name}

### Lists
Use enumerate with [nosep,label=(\roman*)] for parameter conditions.
Use enumerate with [nosep,label=(\alph*)] for result parts.
Use enumerate with [nosep] for numbered contributions in the introduction.

### Available Custom Commands (defined in the preamble)
  \E        → expectation (blackboard E)
  \R        → reals (blackboard R)
  \N        → naturals (blackboard N)
  \Prob     → probability (blackboard P)
  \Var      → variance
  \Cov      → covariance
  \argmax   → arg max (with limits)
  \argmin   → arg min (with limits)
  \supp     → support

### Typography Conventions
- Use ``...'' for LaTeX double quotes (not "...")
- Use --- for em-dashes
- Use -- for en-dashes in ranges and compound adjectives
- Use \emph{} for emphasis, never \textit{} or \textbf{} in running text
- Use \citet{} for textual citations, \citep{} for parenthetical
- Use \citeauthor{} when referring to authors without year
"""


def build_critique_paper_prompt(
    paper_text: str,
    critique_text: str,
    *,
    page_target: int = 6,
    additional_instructions: str = "",
) -> str:
    """Build the prompt for the critique-based paper generation workflow.

    The model receives:
      1. The original paper text.
      2. The user's critique of that paper.

    It must then produce a short, formal theory paper that:
      - Checks the logical soundness of every argument in the critique.
      - Formalises informal claims into propositions with proofs.
      - Improves exposition and adds structure.
      - Corrects the critique where it is wrong.

    Parameters
    ----------
    paper_text : str
        Full text of the original paper being critiqued.
    critique_text : str
        The user's critique / notes on the paper.
    page_target : int
        Target page count for the output paper.
    additional_instructions : str
        Any extra guidance from the user.
    """
    sections = [
        f"You are given an original paper and a critique of that paper.",
        f"Your task: write a short, self-contained theory paper in LaTeX "
        f"(~{page_target} pages of body content) that formalises the critique "
        f"into a rigorous contribution.",
        "",
        "## Your Responsibilities",
        "1. **Logical audit** — For every argument in the critique, check "
        "whether it is logically sound. If an argument is flawed, state "
        "why and provide the correct result.",
        "2. **Formalisation** — Convert informal claims into formal "
        "propositions, lemmas, or theorems with proofs or proof sketches.",
        "3. **Model construction** — If the critique implies a model "
        "different from the original paper, build that model explicitly "
        "(primitives, agents, constraints, information, timing).",
        "4. **Exposition** — Write clear, precise prose connecting the "
        "formal results. No fluff, no hand-waving.",
        "5. **Honesty** — If the critique is wrong on a point, say so "
        "and prove the correct claim. If the original paper is right "
        "and the critique is mistaken, acknowledge it.",
        "",
        "## Original Paper",
        "--- BEGIN PAPER ---",
        paper_text,
        "--- END PAPER ---",
        "",
        "## Critique",
        "--- BEGIN CRITIQUE ---",
        critique_text,
        "--- END CRITIQUE ---",
    ]

    if additional_instructions:
        sections += [
            "",
            f"## Additional Instructions",
            additional_instructions,
        ]

    sections += [
        "",
        "## Structure Requirements",
        "The output paper MUST use exactly these sections, in this order:",
        "1. \\section{Introduction} — state what the original paper claims, "
        "what the critique argues, and what this paper establishes. "
        "If the contribution has multiple parts, list them with "
        "\\begin{enumerate}[nosep]. No fluff.",
        "2. \\section{Model} — the formal environment. State all primitives "
        "using the assumption environment (e.g., \\begin{assumption}[Technology]). "
        "Define contracts/mechanisms using the definition environment. "
        "If the critique uses the same model as the original paper, "
        "restate it precisely. If the critique modifies it, define the "
        "modified model.",
        "3. \\section{Analysis} — formal propositions with proofs addressing "
        "each point of the critique. Use \\subsection{} to organise by "
        "claim or topic. Intersperse remarks for interpretation.",
        "4. \\section{Discussion} — summarise which parts of the critique "
        "survive, which fail, and what the net conclusion is. "
        "Discuss policy implications if relevant.",
        "5. (Optional) \\appendix with longer proofs if needed.",
        "",
        "Do NOT add other top-level sections. Do NOT rename these sections.",
        "",
        "## Formatting Rules",
        "- Output ONLY the LaTeX body (sections, theorems, proofs). "
        "No preamble, no \\begin{document}.",
        "- Every proposition must have a proof or proof sketch.",
        "- Every variable must be defined before use.",
        "- Label all environments with \\label{} using the convention: "
        "a: for assumptions, d: for definitions, p: for propositions, "
        "eq: for equations, r: for remarks.",
        "- Use \\cref{} for all cross-references (not \\ref{}).",
        "- Use \\citet{} and \\citep{} for citations.",
        "- Do NOT fabricate citations. If you are unsure a reference exists, "
        "omit it.",
    ]

    return "\n".join(sections)


def build_abstract_prompt(body: str) -> str:
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


def build_title_prompt(abstract: str) -> str:
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
