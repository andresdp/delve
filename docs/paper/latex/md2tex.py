"""One-time conversion of docs/paper/SANER2027_Delve_Draft.md to IEEEtran LaTeX (sections 1-8)."""
import re
import subprocess
import sys

MD = "docs/paper/SANER2027_Delve_Draft.md"
OUT = "docs/paper/latex/main.tex"
KEYS = ["shaw", "qoc", "jansenbosch", "kruchten", "garousi", "warnett", "fang", "stol", "tnt", "lloom", "dhar",
        "lma", "bhat", "soliman", "saslr", "nelson", "xiao", "chew", "ahmed", "chainoflayer", "bertopic", "llm4se",
        "judge"]

md = open(MD, encoding="utf-8").read()
# sanity: the reference list order matches KEYS
refs = md[md.index("## References"):md.index("## 9. Author Notes")]
checks = {1: "Shaw", 6: "Warnett", 9: "TnT-LLM", 12: "Multi-Agent", 20: "Chain-of-Layer", 21: "BERTopic",
          22: "Large Language Models for Software Engineering", 23: "Judging LLM"}
for n, needle in checks.items():
    line = re.search(rf"^{n}\. (.*)$", refs, re.M).group(1)
    assert needle in line, (n, line[:60])

abstract = md[md.index("## Abstract") + len("## Abstract"):md.index("**Keywords:**")].strip()
keywords = re.search(r"\*\*Keywords:\*\* (.*)", md).group(1).strip().rstrip(".")
body = md[md.index("## 1. Introduction"):md.index("## References")]


def prep(text: str) -> str:
    # pandoc needs a blank line before a list that follows a paragraph line
    text = re.sub(r"(?m)^(?!\s*(?:[-*] |\d+\. )|\s*$)(.+)\n(\s*(?:[-*] |\d+\. ))", r"\1\n\n\2", text)
    text = re.sub(r"^## \d+\. (.*)$", r"# \1", text, flags=re.M)
    text = re.sub(r"^### \d+\.\d+ (.*)$", r"## \1", text, flags=re.M)
    text = text.replace("# Results — Pending Evaluation", "# Results")
    text = re.sub(r"\[(\d+(?:, \d+)*)\](?!\()",
                  lambda m: "⟦CITE:" + ",".join(KEYS[int(n) - 1] for n in m.group(1).split(", ")) + "⟧", text)
    text = re.sub(r"\[TODO: ([^\]]*)\]", r"⟦TODO:\1⟧", text)
    text = re.sub(r"!\[Figure 1\]\([^)]*\)\n\n\*\*Fig\. 1\.\*\*[^\n]*\n", "⟦FIG1⟧\n", text)
    return text


def pandoc(text: str) -> str:
    out = subprocess.run(["pandoc", "-f", "markdown-auto_identifiers", "-t", "latex", "--wrap=none"],
                         input=text, capture_output=True, text=True, check=True).stdout
    out = re.sub(r"⟦CITE:([^⟧]*)⟧", r"\\cite{\1}", out)
    out = re.sub(r"⟦TODO:([^⟧]*)⟧", r"\\todo{\1}", out)
    for a, b in [("≥", r"$\geq$"), ("≤", r"$\leq$"), ("×", r"$\times$"), ("→", r"$\rightarrow$"),
                 ("κ", r"$\kappa$")]:
        out = out.replace(a, b)
    return out


tex_body = pandoc(prep(body))

FIG1 = r"""\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/fig1-delve-workflow.pdf}
  \caption{Delve: its inputs (left), the workflow with its four LLM roles (center), and its outputs (right). The open- and axial-coding loop runs once per minibatch until the Critic's coverage check holds for $k$ minibatches in a row. Dashed boxes are deterministic steps; dashed arrows carry feedback.}
  \label{fig:workflow}
\end{figure*}"""

TABLE_ROLES = r"""\begin{table}[t]
  \centering
  \caption{Delve's roles and how each one works.}
  \label{tab:roles}
  \footnotesize
  \begin{tabular}{@{}L{0.17\columnwidth}L{0.36\columnwidth}L{0.38\columnwidth}@{}}
    \toprule
    Role & Responsibility & Mechanism \\
    \midrule
    Coder & Extract passage-level concepts and the source's stance & Structured LLM output per passage \\
    Taxonomist & Build and revise decision points, alternatives and relations; review the final model & First draft as structured output; updates and review through validated editing operations, each logged \\
    Critic & Score drafts; detect concepts the model does not yet cover & LLM scoreboard fed back to the next update; coverage check of each new minibatch (read-only) \\
    Integrator & Consolidate and scope the reviewed model & Dimension merging and value consolidation (embedding candidates, LLM adjudication of borderline pairs), evidence linking, minimum-support selection, labeling \\
    \bottomrule
  \end{tabular}
\end{table}"""

TABLE_CASES = r"""\begin{table}[t]
  \centering
  \caption{Cases and corpora.}
  \label{tab:cases}
  \footnotesize
  \begin{tabular}{@{}L{0.30\columnwidth}L{0.24\columnwidth}rrr@{}}
    \toprule
    Case & Expert reference & Sources & Passages & Words \\
    \midrule
    C1: ML workflow & Paper and replication model~\cite{warnett} & 29 / 29 & 265 & 70,191 \\
    C2: deployed RL monitoring & Paper and replication model~\cite{fang} & 27 / 29 & 243 & 61,980 \\
    C3: Git hosting at scale & None & 5 / 5 & 48 & 13,817 \\
    \bottomrule
  \end{tabular}

  \smallskip
  \raggedright\scriptsize Sources: usable / listed.
\end{table}"""

tables = re.findall(r"\\begin\{longtable\}.*?\\end\{longtable\}", tex_body, flags=re.S)
assert len(tables) == 2, len(tables)
tex_body = tex_body.replace(tables[0], TABLE_ROLES).replace(tables[1], TABLE_CASES)
tex_body = tex_body.replace("⟦FIG1⟧", FIG1)
# Refer to the figure and tables by label.
tex_body = tex_body.replace("Figure 1 shows the workflow.", r"Fig.~\ref{fig:workflow} shows the workflow and Table~\ref{tab:roles} the roles.")
tex_body = tex_body.replace("Section 4.4", r"Section~\ref{sec:baselines}").replace("Section 4.7", r"Section~\ref{sec:c3}")
tex_body = tex_body.replace(r"\subsection{Baselines and ablations}", r"\subsection{Baselines and ablations}\label{sec:baselines}")
tex_body = tex_body.replace(r"\subsection{The Git-hosting case}", r"\subsection{The Git-hosting case}\label{sec:c3}")
tex_body = tex_body.replace(r"\subsection{Cases and corpora}", r"\subsection{Cases and corpora}" + "\nTable~\\ref{tab:cases} summarizes the cases.")
tex_abstract = pandoc(prep(abstract)).strip()

PREAMBLE = r"""\documentclass[conference]{IEEEtran}
% SANER 2027 Agentic AI4SE track: 10 pages + 2 pages of references, double-anonymous.
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\usepackage{xcolor}
\usepackage{cite}
\usepackage{url}
\usepackage[hidelinks]{hyperref}

% Pandoc list spacing.
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
% Open items: remove every \todo before submission (\renewcommand{\todo}[1]{} hides them).
\newcommand{\todo}[1]{{\color{red}\textbf{[TODO:}~#1\textbf{]}}}

\begin{document}

\title{Delve: An Agentic Workflow for Mining Architectural Design Spaces from Practitioner Literature}

\author{\IEEEauthorblockN{Anonymous Author(s)}
\IEEEauthorblockA{Affiliation withheld for double-anonymous review}}

\maketitle

\begin{abstract}
"""

doc = (PREAMBLE + tex_abstract + "\n\\end{abstract}\n\n\\begin{IEEEkeywords}\n" + keywords + "\n\\end{IEEEkeywords}\n\n"
       + tex_body.strip() + "\n\n\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n\n\\end{document}\n")
open(OUT, "w", encoding="utf-8").write(doc)
print("written", OUT, len(doc.split()), "words (incl. markup)")
