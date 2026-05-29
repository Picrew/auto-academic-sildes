from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .assets import crop_asset, resolve_asset
from .content import Slide
from .ir import Deck, DEFAULT_DECK


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def visual_image_path(s: Slide, deck: Deck) -> Path | None:
    evidence = s.evidence
    image_name = evidence.image if evidence and evidence.image else s.image
    if not image_name:
        return None
    source = resolve_asset(deck, image_name)
    if not source.exists():
        return None
    if evidence and evidence.crop:
        key = slug(f"{s.kicker}-{s.title}-{image_name}")[:48] or "crop"
        cache_root = Path(deck.base_dir).resolve() if deck.base_dir else Path.cwd()
        return crop_asset(source, evidence.crop, cache_root / "asset-cache", key)
    return source


def frame_header(s: Slide) -> str:
    return rf"""
\begin{{frame}}[t]
\kicker{{{tex_escape(s.kicker)}}}
\frametitle{{{tex_escape(s.title)}}}
"""


def bullets(items: tuple[str, ...]) -> str:
    if not items:
        return ""
    body = "\n".join(rf"\item {tex_escape(item)}" for item in items)
    return rf"\begin{{itemize}}{body}\end{{itemize}}"


def metrics(items: tuple[tuple[str, str], ...]) -> str:
    if not items:
        return ""
    cells = []
    for value, label in items:
        cells.append(rf"\metric{{{tex_escape(value)}}}{{{tex_escape(label)}}}")
    return r"\begin{metricrow}" + "\n".join(cells) + r"\end{metricrow}"


def cover_metrics(items: tuple[tuple[str, str], ...]) -> str:
    if not items:
        return ""
    cells = []
    for value, label in items:
        cells.append(rf"\covermetric{{{tex_escape(value)}}}{{{tex_escape(label)}}}")
    return r"\begin{metricrow}" + "\n".join(cells) + r"\end{metricrow}"


def visual_for(s: Slide, deck: Deck) -> str:
    if s.kind == "map":
        nodes = " / ".join(s.labels)
        loop = " -> ".join(s.labels[:4]) if len(s.labels) >= 4 else "failure -> signal -> policy -> system"
        return rf"""
\begin{{artifactbox}}
\Large {tex_escape(nodes)}
\par\vspace{{0.8em}}\small {tex_escape(loop)}
\end{{artifactbox}}
"""
    if s.kind == "process":
        rows = "\n".join(rf"\phase{{{i+1:02d}}}{{{tex_escape(label)}}}" for i, label in enumerate(s.labels))
        return rf"\begin{{processgrid}}{rows}\end{{processgrid}}"
    if s.kind == "matrix":
        rows = "\n".join(rf"\tagpill{{{tex_escape(label)}}}" for label in s.labels)
        return rf"\begin{{pillgrid}}{rows}\end{{pillgrid}}"
    if s.kind == "system":
        return r"""
\begin{artifactbox}
\centering
\sysnode{text} \arrow \sysnode{face position}\\[0.7em]
\sysnode{shape VAE} \arrow \sysnode{edge diffusion}\\[0.7em]
\sysnode{valid B-Rep CAD}
\end{artifactbox}
"""
    if s.kind == "loop":
        return r"""
\begin{artifactbox}
\centering\Large benchmark $\rightarrow$ bad cases $\rightarrow$ train $\rightarrow$ gate
\end{artifactbox}
"""
    image_path = visual_image_path(s, deck)
    if image_path:
        if image_path.exists():
            return rf"\includegraphics[width=\linewidth,height=0.47\paperheight,keepaspectratio]{{{image_path.as_posix()}}}"
    return metrics(s.metrics)


def render_slide(s: Slide, i: int, deck: Deck) -> str:
    if s.kind == "cover":
        return rf"""
\begin{{frame}}[plain]
\begin{{tikzpicture}}[remember picture,overlay]
  \fill[graphite] (current page.south west) rectangle (current page.north east);
  \draw[copper,line width=0.7pt] ([xshift=0.62cm,yshift=-0.62cm]current page.north west) -- ([xshift=-0.62cm,yshift=-0.62cm]current page.north east);
\end{{tikzpicture}}
\vspace*{{0.72cm}}
{{\mono\small\color{{copper}} {tex_escape(s.kicker.upper() or "RESEARCH DECK")}}}\par\vspace{{0.28cm}}
{{\displayfont\fontsize{{36}}{{38}}\selectfont\color{{paper}} {tex_escape(deck.title)}}}\par\vspace{{0.16cm}}
{{\displayfont\fontsize{{26}}{{29}}\selectfont\color{{paper}} {tex_escape(s.title)}}}\par
{{\displayfont\fontsize{{16}}{{19}}\selectfont\color{{softtext}} {tex_escape(deck.subtitle)}}}\par\vspace{{0.58cm}}
{{\large\color{{softtext}} {tex_escape(s.subtitle)}}}\par\vfill
{cover_metrics(s.metrics)}
\vspace{{0.38cm}}
\hairlineDark
\end{{frame}}
"""
    left = bullets(s.bullets)
    right = visual_for(s, deck)
    subtitle = rf"\subtitleline{{{tex_escape(s.subtitle)}}}" if s.subtitle else ""
    return frame_header(s) + subtitle + rf"""
\begin{{columns}}[T,totalwidth=\textwidth]
\column{{0.48\textwidth}}
{left}
\column{{0.48\textwidth}}
{right}
\end{{columns}}
\end{{frame}}
"""


def build_tex(deck: Deck | None = None) -> str:
    deck = deck or DEFAULT_DECK
    slides = "\n".join(render_slide(s, i, deck) for i, s in enumerate(deck.slides, start=1))
    footer = tex_escape(deck.footer or deck.title)
    return rf"""
\documentclass[10pt,aspectratio=169,t]{{beamer}}
\usepackage{{fontspec}}
\usepackage{{graphicx}}
\usepackage{{tikz}}
\usepackage{{tabularx}}
\usepackage{{ragged2e}}
\usetikzlibrary{{positioning,calc,arrows.meta}}
\setbeamertemplate{{navigation symbols}}{{}}
\setbeamertemplate{{frametitle}}{{%
  \vspace{{0.04cm}}
  {{\displayfont\fontsize{{23}}{{26}}\selectfont\color{{ink}}\insertframetitle}}\par
  \vspace{{0.10cm}}\textcolor{{hair}}{{\rule{{\linewidth}}{{0.45pt}}}}\par
  \vspace{{0.26cm}}
}}
\definecolor{{paper}}{{HTML}}{{F5F1E8}}
\definecolor{{ink}}{{HTML}}{{101418}}
\definecolor{{muted}}{{HTML}}{{5D6773}}
\definecolor{{hair}}{{HTML}}{{D9D0C2}}
\definecolor{{copper}}{{HTML}}{{A45B2A}}
\definecolor{{teal}}{{HTML}}{{0E7C7B}}
\definecolor{{graphite}}{{HTML}}{{151A20}}
\definecolor{{softtext}}{{HTML}}{{C7D1D8}}
\setbeamercolor{{background canvas}}{{bg=paper}}
\setbeamercolor{{normal text}}{{fg=ink}}
\setsansfont{{Helvetica Neue}}
\setmainfont{{Georgia}}
\newfontfamily\displayfont{{Georgia}}
\newfontfamily\mono{{Menlo}}
\setbeamersize{{text margin left=0.58cm,text margin right=0.58cm}}
\setbeamertemplate{{footline}}{{%
  \ifnum\value{{framenumber}}>1
  \begin{{beamercolorbox}}[wd=\paperwidth,ht=2.4ex,dp=1.0ex,leftskip=0.58cm,rightskip=0.58cm]{{footline}}
    {{\scriptsize\color{{muted}}{footer}}}\hfill{{\scriptsize\color{{muted}}\insertframenumber/\inserttotalframenumber}}
  \end{{beamercolorbox}}
  \fi
}}
\newcommand{{\kicker}}[1]{{\vspace{{0.28cm}}{{\mono\fontsize{{8}}{{10}}\selectfont\bfseries\color{{copper}}\MakeUppercase{{#1}}}}\par\vspace{{0.06cm}}}}
\newcommand{{\subtitleline}}[1]{{{{\small\color{{muted}}#1}}\par\vspace{{0.34cm}}}}
\newcommand{{\hairlineDark}}{{\textcolor{{softtext}}{{\rule{{\linewidth}}{{0.4pt}}}}}}
\newcommand{{\metric}}[2]{{\begin{{minipage}}{{0.3\linewidth}}{{\displayfont\fontsize{{20}}{{22}}\selectfont\color{{ink}}#1}}\par{{\scriptsize\color{{muted}}#2}}\end{{minipage}}\hfill}}
\newcommand{{\covermetric}}[2]{{\begin{{minipage}}{{0.3\linewidth}}{{\displayfont\fontsize{{20}}{{22}}\selectfont\color{{paper}}#1}}\par{{\scriptsize\color{{softtext}}#2}}\end{{minipage}}\hfill}}
\newenvironment{{metricrow}}{{\par}}{{\par}}
\newcommand{{\phase}}[2]{{\begin{{minipage}}{{0.31\linewidth}}\raggedright{{\mono\scriptsize\color{{copper}}#1}}\par{{\large #2}}\end{{minipage}}\hfill}}
\newenvironment{{processgrid}}{{\begin{{artifactbox}}}}{{\end{{artifactbox}}}}
\newcommand{{\tagpill}}[1]{{\fboxsep=0.45em\colorbox{{graphite}}{{\color{{paper}}\mono\scriptsize #1}}\hspace{{0.3em}}\vspace{{0.5em}}}}
\newenvironment{{pillgrid}}{{\begin{{artifactbox}}\RaggedRight}}{{\end{{artifactbox}}}}
\newcommand{{\sysnode}}[1]{{\fboxsep=0.45em\colorbox{{paper}}{{\mono\scriptsize #1}}}}
\newcommand{{\arrow}}{{\hspace{{0.4em}}\textcolor{{copper}}{{$\rightarrow$}}\hspace{{0.4em}}}}
\newenvironment{{artifactbox}}{{%
  \begin{{beamercolorbox}}[wd=\linewidth,sep=0.28cm,rounded=false]{{artifact}}
}}{{\end{{beamercolorbox}}}}
\setbeamercolor{{artifact}}{{bg=white,fg=ink}}
\setbeamerfont{{frametitle}}{{family=\displayfont,size=\fontsize{{24}}{{27}}\selectfont}}
\setbeamertemplate{{itemize item}}{{\color{{copper}}\scriptsize$\blacktriangleright$}}
\setlength{{\leftmargini}}{{1.05em}}
\begin{{document}}
{slides}
\end{{document}}
"""


def render_beamer(output_dir: Path, compile_pdf: bool = True, deck: Deck | None = None) -> tuple[Path, Path | None]:
    output_dir.mkdir(parents=True, exist_ok=True)
    deck = deck or DEFAULT_DECK
    safe = slug(deck.deck_id or deck.title) or "academic-deck"
    tex_path = output_dir / f"{safe}-beamer.tex"
    tex_path.write_text(build_tex(deck), encoding="utf-8")
    pdf_path = output_dir / f"{safe}-beamer.pdf"
    if compile_pdf:
        for _ in range(2):
            subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
                cwd=output_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        produced = output_dir / f"{tex_path.stem}.pdf"
        if produced.exists() and produced != pdf_path:
            produced.replace(pdf_path)
    return tex_path, pdf_path if pdf_path.exists() else None
