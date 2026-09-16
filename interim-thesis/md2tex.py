"""
中間論文の Markdown ドラフトを LaTeX に変換する。

出力は tex/ 以下。章ごとのファイルと、単体でコンパイルできる main.tex を作る。
指定フォーマットのテンプレートがある場合は、章ファイルだけを差し込めばよい。

使い方:
  python md2tex.py

変換の対象と方針:
  # 第1章 序論     → \chapter{序論}
  ## 1.1 背景      → \section{背景}
  ### 1.1.1 ...    → \subsection{...}
  **強調**         → \textbf{...}
  `コード`         → \texttt{...}
  [1][2]           → \cite{key1,key2}（09-references.md の対応表を使う）
  表 5.1 ...       → table 環境（キャプションは表の上）
  図 5.1 ...       → figure 環境（キャプションは図の下）
  $$ ... $$        → equation 環境
  ``` ... ```      → quote + verbatim
  - 項目           → itemize
  1. 項目          → enumerate

注意:
  - 本文の「，．」はそのまま出力する。
  - TeX の特殊文字（% & _ # $ ~ ^ \）は数式の外でのみ escape する。
  - 生成物は必ず目視で確認すること。この変換器は本ドラフト専用であり、
    Markdown 一般を正しく扱うものではない。
"""

from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).parent
OUT = SRC / "tex"

CHAPTERS = [
    ("01-abstract.md", "abstract.tex", None),
    ("02-chapter1-introduction.md", "chapter1.tex", "序論"),
    ("03-chapter2-related-work.md", "chapter2.tex", "関連研究"),
    ("04-chapter3-design.md", "chapter3.tex", "設計方針"),
    ("05-chapter4-implementation.md", "chapter4.tex", "実装"),
    ("06-chapter5-experiment.md", "chapter5.tex", "予備実験"),
    ("07-chapter6-discussion.md", "chapter6.tex", "考察"),
    ("08-chapter7-future-work.md", "chapter7.tex", "今後の方針"),
]

# 図番号 → (出力するファイル名, 元のファイル名, 幅)
# ファイル名にアンダースコアを使わない。\includegraphics の引数で
# 扱いが面倒になるうえ、元の fig1/fig2 という名前は図 5.1／5.2 と
# 番号が逆で取り違えやすいため、内容がわかる名前に変える。
FIGURES = {
    "5.1": ("confidence-distribution", "fig2_confidence", 1.0),
    "5.2": ("reliability-diagram", "fig1_reliability", 0.7),
}


def load_citation_map() -> dict[str, str]:
    """09-references.md から [番号] → BibTeX キーの対応を作る。"""
    text = (SRC / "09-references.md").read_text(encoding="utf-8")
    mapping: dict[str, str] = {}
    num = None
    for line in text.splitlines():
        m = re.match(r"^\[(\d+)\]", line)
        if m:
            num = m.group(1)
        if num:
            k = re.search(r"`([a-z0-9]+)`", line)
            if k:
                mapping[num] = k.group(1)
                num = None
    return mapping


def _is_ascii_word(ch: str) -> bool:
    """英数字と、英単語の一部になりうる記号か。"""
    return ch.isascii() and (ch.isalnum() or ch in "-_.,:;)]}\"'")


def escape(text: str) -> str:
    """数式の外で TeX の特殊文字を escape する。"""
    out = []
    for i, part in enumerate(re.split(r"(\$[^$]*\$)", text)):
        if i % 2 == 1:  # $...$ の中はそのまま
            out.append(part)
            continue
        part = part.replace("\\", r"\textbackslash{}")
        for ch, rep in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
                        ("_", r"\_"), ("{", r"\{"), ("}", r"\}")]:
            part = part.replace(ch, rep)
        part = part.replace("~", r"\textasciitilde{}")
        part = part.replace("^", r"\textasciicircum{}")
        out.append(part)
    return "".join(out)


def inline(text: str, cites: dict[str, str]) -> str:
    """行内の記法を変換する。escape のあとに適用する。"""
    # 引用 [1][2] → \cite{a,b}（連続するものはまとめる）
    def cite_run(m: re.Match) -> str:
        nums = re.findall(r"\[(\d+)\]", m.group(0))
        keys = [cites[n] for n in nums if n in cites]
        return "\\cite{" + ",".join(keys) + "}" if keys else m.group(0)

    text = re.sub(r"(?:\[\d+\])+", cite_run, text)
    # コードは escape 済みの記号を戻したいので \verb ではなく \texttt を使う
    text = re.sub(r"`([^`]+)`", lambda m: r"\texttt{" + m.group(1) + "}", text)
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: r"\textbf{" + m.group(1) + "}", text)
    return text


def convert_table(caption: str, rows: list[str], label: str) -> list[str]:
    """Markdown の表を tabular にする。キャプションは表の上に置く。"""
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], cells[2:]  # cells[1] は区切り行
    ncol = len(header)
    spec = "|" + "l|" * ncol
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\small",
        f"\\caption{{{caption}}}",
        f"\\label{{tab:{label}}}",
        f"\\begin{{tabular}}{{{spec}}}",
        r"\hline",
        " & ".join(header) + r" \\",
        r"\hline",
    ]
    for row in body:
        row = (row + [""] * ncol)[:ncol]
        lines.append(" & ".join(row) + r" \\")
    lines += [r"\hline", r"\end{tabular}", r"\end{table}", ""]
    return lines


def flow_figure(lines: list[str], caption: str, num: str,
                cites: dict[str, str]) -> list[str]:
    """矢印で繋いだ流れ図を figure として組む。"""
    steps: list[str] = []
    for raw in lines:
        t = raw.strip()
        if not t or t == "↓":
            continue
        steps.append(inline(escape(t), cites))
    out = [
        r"\begin{figure}[htbp]",
        r"\centering",
        r"\begin{tabular}{c}",
    ]
    for k, step in enumerate(steps):
        out.append(r"\fbox{\parbox{0.75\linewidth}{\centering " + step + r"}} \\")
        if k != len(steps) - 1:
            out.append(r"$\downarrow$ \\")
    out += [
        r"\end{tabular}",
        f"\\caption{{{inline(escape(caption), cites)}}}",
        f"\\label{{fig:{num}}}",
        r"\end{figure}",
        "",
    ]
    return out


def convert(path: Path, cites: dict[str, str], chapter_title: str | None) -> str:
    src = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    para: list[str] = []
    list_mode: str | None = None

    def join_lines(parts: list[str]) -> str:
        """原稿の折り返しを連結する。

        日本語どうしはそのまま繋ぐが、英数字どうしが隣り合う場合は空白を
        入れる。原稿は読みやすさのために英語表記の途中で改行しており、
        そのまま繋ぐと「Expected」と「Calibration」が繋がってしまう。
        """
        buf = parts[0]
        for nxt in parts[1:]:
            if buf and nxt and _is_ascii_word(buf[-1]) and _is_ascii_word(nxt[0]):
                buf += " "
            buf += nxt
        return buf

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(join_lines(para))
            out.append("")
            para = []

    def close_list() -> None:
        nonlocal list_mode
        if list_mode:
            out.append(f"\\end{{{list_mode}}}")
            out.append("")
            list_mode = None

    while i < len(src):
        line = src[i]
        stripped = line.strip()

        # 見出し
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_para(); close_list()
            level, title = len(m.group(1)), m.group(2)
            title = re.sub(r"^第\d+章\s*", "", title)
            title = re.sub(r"^\d+(\.\d+)*\s*", "", title)
            title = inline(escape(title), cites)
            if level == 1:
                out.append(f"\\chapter{{{title}}}" if chapter_title else "")
            elif level == 2:
                out.append(f"\\section{{{title}}}")
            elif level == 3:
                out.append(f"\\subsection{{{title}}}")
            else:
                out.append(f"\\subsubsection{{{title}}}")
            out.append("")
            i += 1
            continue

        # 数式ブロック
        if stripped == "$$":
            flush_para(); close_list()
            i += 1
            eq = []
            while i < len(src) and src[i].strip() != "$$":
                eq.append(src[i])
                i += 1
            i += 1
            out.append(r"\begin{equation}")
            out.extend(eq)
            out.append(r"\end{equation}")
            out.append("")
            continue

        # コードブロック（プロンプト例・処理フロー）
        if stripped.startswith("```"):
            flush_para(); close_list()
            i += 1
            code = []
            while i < len(src) and not src[i].strip().startswith("```"):
                code.append(src[i])
                i += 1
            i += 1
            if any("↓" in c for c in code):
                # 流れ図。直後の図キャプションと合わせて figure にする。
                # verbatim に日本語と矢印を入れると等幅フォント側の都合で
                # 崩れやすいため、表として組む。
                flow = code
                cap = "評価の処理フロー"
                num = "3.1"
                j = i
                while j < len(src) and not src[j].strip():
                    j += 1
                m2 = re.match(r"^図\s*(\d+\.\d+)\s+(.*)$", src[j].strip()) if j < len(src) else None
                if m2:
                    num, cap = m2.group(1), m2.group(2)
                    i = j + 1
                out.extend(flow_figure(flow, cap, num, cites))
                continue
            out.append(r"\begin{quote}")
            out.append(r"\begin{verbatim}")
            out.extend(code)
            out.append(r"\end{verbatim}")
            out.append(r"\end{quote}")
            out.append("")
            continue

        # 表（キャプション行 → 空行 → 表本体）
        m = re.match(r"^表\s*(\d+\.\d+)\s+(.*)$", stripped)
        if m:
            j = i + 1
            while j < len(src) and not src[j].strip().startswith("|"):
                j += 1
            if j < len(src):
                rows = []
                while j < len(src) and src[j].strip().startswith("|"):
                    rows.append(inline(escape(src[j]), cites))
                    j += 1
                flush_para(); close_list()
                out.extend(convert_table(inline(escape(m.group(2)), cites),
                                         rows, m.group(1)))
                i = j
                continue

        # 図
        m = re.match(r"^図\s*(\d+\.\d+)\s+(.*)$", stripped)
        if m:
            flush_para(); close_list()
            num, cap = m.group(1), inline(escape(m.group(2)), cites)
            if num in FIGURES:
                fname, _src, width = FIGURES[num]
                out += [
                    r"\begin{figure}[htbp]", r"\centering",
                    f"\\includegraphics[width={width}\\linewidth]{{figures/{fname}}}",
                    f"\\caption{{{cap}}}", f"\\label{{fig:{num}}}",
                    r"\end{figure}", "",
                ]
            else:
                # 図 3.1 は未作成。差し替え位置を残す
                out += [
                    r"\begin{figure}[htbp]", r"\centering",
                    r"\fbox{\parbox{0.8\linewidth}{\centering\vspace{3zw}"
                    r"（作図して差し替える）\vspace{3zw}}}",
                    f"\\caption{{{cap}}}", f"\\label{{fig:{num}}}",
                    r"\end{figure}", "",
                ]
            i += 1
            continue

        # 箇条書き
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_mode != "itemize":
                close_list()
                out.append(r"\begin{itemize}")
                list_mode = "itemize"
            out.append(r"\item " + inline(escape(m.group(1)), cites))
            i += 1
            continue
        m = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m:
            flush_para()
            if list_mode != "enumerate":
                close_list()
                out.append(r"\begin{enumerate}")
                list_mode = "enumerate"
            out.append(r"\item " + inline(escape(m.group(1)), cites))
            i += 1
            continue

        # 引用（> で始まる注記）
        if stripped.startswith(">"):
            flush_para(); close_list()
            out.append(r"\begin{quote}")
            while i < len(src) and src[i].strip().startswith(">"):
                out.append(inline(escape(src[i].strip().lstrip("> ")), cites))
                i += 1
            out.append(r"\end{quote}")
            out.append("")
            continue

        # 空行 = 段落の区切り
        if not stripped:
            flush_para(); close_list()
            i += 1
            continue

        # 通常の本文。原稿は途中で改行しているので連結する
        para.append(inline(escape(stripped), cites))
        i += 1

    flush_para(); close_list()
    return "\n".join(out).replace("\n\n\n", "\n\n").strip() + "\n"


MAIN = r"""%% 中間論文（夏の中間報告）
%%
%% Overleaf でのコンパイル設定:
%%   Compiler: LaTeX  (uplatex + dvipdfmx)
%%   Main document: main.tex
%%
%% 研究室指定のフォーマットがある場合は、この main.tex は使わず、
%% chapter1.tex 〜 chapter7.tex と abstract.tex をテンプレートに
%% \input で差し込むこと。
\documentclass[uplatex,dvipdfmx,a4paper,11pt]{jsbook}

\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage[dvipdfmx]{hyperref}
\usepackage{pxjahyper}

\title{プロンプト設計による大規模言語モデルの\\キャリブレーション性能向上に関する研究}
\author{7422048 指田 一茶}
\date{2026 年度 中間報告}

\begin{document}

\maketitle

\chapter*{要旨}
\addcontentsline{toc}{chapter}{要旨}
\input{abstract}

\tableofcontents
\listoffigures
\listoftables

\input{chapter1}
\input{chapter2}
\input{chapter3}
\input{chapter4}
\input{chapter5}
\input{chapter6}
\input{chapter7}

\bibliographystyle{junsrt}
\bibliography{references}

\end{document}
"""


def main() -> int:
    OUT.mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    cites = load_citation_map()
    print(f"引用の対応: {len(cites)} 件")

    for src_name, out_name, title in CHAPTERS:
        body = convert(SRC / src_name, cites, title)
        (OUT / out_name).write_text(body, encoding="utf-8")
        print(f"  {src_name} -> tex/{out_name}  ({len(body)} 文字)")

    (OUT / "main.tex").write_text(MAIN, encoding="utf-8")
    print("  tex/main.tex")

    # 図と文献データを tex/ に配置する
    import shutil

    figdir = SRC.parent / "research" / "experiment" / "pilot" / "figures_fixed"
    for _num, (dst, src_name, _w) in FIGURES.items():
        src_path = figdir / f"{src_name}.png"
        if src_path.exists():
            shutil.copy(src_path, OUT / "figures" / f"{dst}.png")
            print(f"  figures/{dst}.png <- {src_name}.png")
        else:
            print(f"  [警告] 図が見つかりません: {src_path}")

    bib = SRC.parent / "research" / "references.bib"
    if bib.exists():
        shutil.copy(bib, OUT / "references.bib")
        print("  tex/references.bib")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
