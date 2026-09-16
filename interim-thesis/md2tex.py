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
OUT = SRC / "overleaf"
TEMPLATE = SRC / "template-src"

# 研究室のテンプレート（jreport・1 段組み・章ごとのフォルダ）に合わせる。
STYLE = "book"
HEADINGS = {
    "article": ["section", "subsection", "subsubsection", "paragraph"],
    "book": ["chapter", "section", "subsection", "subsubsection"],
}

# 原稿 → テンプレート内の配置先
CHAPTERS = [
    ("01-abstract.md", "abstract/abstract.tex", None),
    ("02-chapter1-introduction.md", "chapter1/index1.tex", "序論"),
    ("03-chapter2-related-work.md", "chapter2/index2.tex", "関連研究"),
    ("04-chapter3-design.md", "chapter3/index3.tex", "設計方針"),
    ("05-chapter4-implementation.md", "chapter4/index4.tex", "実装"),
    ("06-chapter5-experiment.md", "chapter5/index5.tex", "予備実験"),
    ("07-chapter6-discussion.md", "chapter6/index6.tex", "考察"),
    ("08-chapter7-future-work.md", "chapter7/index7.tex", "今後の方針"),
]

# 図番号 → (出力するファイル名, 元のファイル名, 幅)
# ファイル名にアンダースコアを使わない。\includegraphics の引数で
# 扱いが面倒になるうえ、元の fig1/fig2 という名前は図 5.1／5.2 と
# 番号が逆で取り違えやすいため、内容がわかる名前に変える。
# 図番号 → (出力名, 元のファイル名, 幅, 2段抜きにするか)
# 確信度の分布は横長（3 対 1 程度）で、2 段組みの 1 段に入れると潰れて
# 読めないため 2 段抜きにする。
# 図番号 → (出力名, 元のファイル名, 幅の指定)
# テンプレートの流儀に合わせて ./figure/ に置き、幅は cm で指定する。
FIGURES = {
    "5.1": ("confidence-distribution", "fig2_confidence", "14cm"),
    "5.2": ("reliability-diagram", "fig1_reliability", "11cm"),
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
    text = re.sub(r"`([^`]+)`", lambda m: r"\texttt{" + _breakable(m.group(1)) + "}", text)
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: r"\textbf{" + m.group(1) + "}", text)
    return text


def _visual_len(cell: str) -> int:
    """おおまかな表示幅。日本語は 2、英数字は 1 として数える。"""
    body = re.sub(r"\\[a-zA-Z]+\{?|\}", "", cell)
    return sum(1 if ch.isascii() else 2 for ch in body)


# 表の幅の目安。テンプレートの本文幅は 30em + 50pt（およそ 14.4cm）で、
# \small で組むと英数字でおよそ 78 文字分に相当する。_visual_len は
# 日本語を 2、英数字を 1 で数えるので、その単位での目安として使う。
PAGE_CAPACITY = 78
# 1 つの列がこれより長い文を含むなら、折り返さないと本文幅を超える
WRAP_THRESHOLD = 24


def _breakable(code: str) -> str:
    r"""等幅で組む文字列に改行可能な位置を入れる。

    \texttt{} の中身は既定では途中で折り返せないため、ファイル名やパスが
    長いと段の外へはみ出す。区切り記号のあとに \allowbreak を入れて
    折り返せるようにする。
    """
    for sep in ("/", r"\_", ".", "-"):
        code = code.replace(sep, sep + r"\allowbreak{}")
    return code


def convert_table(caption: str, rows: list[str], label: str) -> list[str]:
    r"""Markdown の表を LaTeX の表にする。キャプションは表の上に置く。

    本文幅を超えないよう、中身の量に応じて組み方を変える。

      - 長い文を含む列があるなら tabularx の X 列にして折り返す。
        l 列は折り返さないため、そのままでは本文幅を超える。
      - 文は短いが列数が多くて収まらない表は、テンプレートの流儀に合わせて
        \scalebox で縮める。数値が並ぶ表は折り返しても読めない。

    tabularx を使う表があるため、main.tex に \usepackage{tabularx} を
    加えてある。
    """
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    header, body = cells[0], cells[2:]
    ncol = len(header)
    widths = [max(_visual_len(r[k]) for r in [header] + body if k < len(r))
              for k in range(ncol)]
    total = sum(widths) + 2 * ncol  # 罫線と余白の分

    long_cols = [k for k, w in enumerate(widths) if w > WRAP_THRESHOLD]

    lines = [r"\begin{table}[htbp]", r"\centering", r"\small",
             f"\\caption{{{caption}}}", f"\\label{{tab:{label}}}"]

    scale = None
    if long_cols:
        spec = "|" + "|".join("X" if k in long_cols else "l"
                              for k in range(ncol)) + "|"
        open_tag = f"\\begin{{tabularx}}{{\\linewidth}}{{{spec}}}"
        close = r"\end{tabularx}"
    else:
        spec = "|" + "l|" * ncol
        open_tag = f"\\begin{{tabular}}{{{spec}}}"
        close = r"\end{tabular}"
        if total > PAGE_CAPACITY:
            scale = max(0.6, round(PAGE_CAPACITY / total, 2))

    if scale is not None:
        lines.append(f"\\scalebox{{{scale}}}{{")
    lines.append(open_tag)
    lines.append(r"\hline")
    lines.append(" & ".join(header) + r" \\")
    lines.append(r"\hline")
    for row in body:
        row = (row + [""] * ncol)[:ncol]
        lines.append(" & ".join(row) + r" \\")
    lines.append(r"\hline")
    lines.append(close)
    if scale is not None:
        lines.append("}")
    lines += [r"\end{table}", ""]
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
        r"\begin{center}",
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
        r"\end{center}",
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
            cmds = HEADINGS[STYLE]
            if level == 1 and chapter_title is None:
                out.append("")  # 要旨は見出しをテンプレート側に任せる
            else:
                out.append(f"\\{cmds[level - 1]}{{{title}}}")
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
        # 「表 5.1 の差が…」のように本文が表番号で始まる場合があるため、
        # 直後が空行で、その次が表本体であることを確認する。任意の行数を
        # 読み飛ばして探すと、本文をキャプションとして奪ってしまう。
        m = re.match(r"^表\s*(\d+\.\d+)\s+(.*)$", stripped)
        if m:
            j = i + 1
            if j < len(src) and not src[j].strip():
                j += 1
            if j < len(src) and src[j].strip().startswith("|"):
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
                    r"\begin{figure}[htbp]",
                    r"\begin{center}",
                    f"\\includegraphics[width={width}]{{./figure/{fname}.png}}",
                    f"\\caption{{{cap}}}", f"\\label{{fig:{num}}}",
                    r"\end{center}",
                    r"\end{figure}", "",
                ]
            else:
                out += [
                    r"\begin{figure}[htbp]", r"\begin{center}",
                    r"\fbox{\parbox{0.8\linewidth}{\centering\vspace{3zw}"
                    r"（作図して差し替える）\vspace{3zw}}}",
                    f"\\caption{{{cap}}}", f"\\label{{fig:{num}}}",
                    r"\end{center}", r"\end{figure}", "",
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


def build_bibliography() -> str:
    r"""09-references.md から thebibliography 環境を作る。

    BibTeX を走らせずに参考文献を出すためのもの。Overleaf でテンプレートに
    差し込む際、bibtex の実行や \bibliography の記述が漏れると引用がすべて
    [?] になる。thebibliography なら追加の設定なしに出力される。
    """
    text = (SRC / "09-references.md").read_text(encoding="utf-8")
    cites = load_citation_map()

    # [n] から次の [n] までを 1 件として切り出す
    blocks: dict[str, list[str]] = {}
    num: str | None = None
    for line in text.splitlines():
        m = re.match(r"^\[(\d+)\]\s*(.*)$", line)
        if m:
            num = m.group(1)
            blocks[num] = [m.group(2)]
            continue
        if num is None:
            continue
        t = line.strip()
        if not t:
            num = None          # 空行で 1 件終わり
            continue
        if t.startswith("**") or t.startswith("※"):
            num = None          # 注記以降はその項目の対象外にする
            continue
        blocks[num].append(t)

    lines = [r"\begin{thebibliography}{99}", r"{\normalsize", ""]
    for n in sorted(blocks, key=int):
        key = cites.get(n)
        if not key:
            continue
        body = " ".join(blocks[n])
        body = re.sub(r"`[a-z0-9]+`", "", body).strip()   # BibTeX キーを除く
        body = escape(body)
        body = re.sub(r"https?://[^\s]+", lambda m: r"\url{" + m.group(0) + "}",
                      body)
        lines.append(f"\\bibitem{{{key}}} {body}")
        lines.append("")
    lines += ["", "}", r"\end{thebibliography}"]
    return "\n".join(lines) + "\n"


TITLE = r"""\begin{titlepage}

\title{\flushleft{\vspace{-3cm}\small{2026年度~~卒業研究~~中間報告}}\\\vspace{3.5cm}
\center{{\huge \bf

プロンプト設計による大規模言語モデルの \\
キャリブレーション性能向上に関する研究 \\

}}\vfill}

\author{
\rightline{東京理科大学~~創域理工学部~~経営システム工学科}\\
\rightline{秦野研究室~~7422048~~指田~~一茶}\\
\rightline{}\\
\rightline{指導教員~~~秦野~~亮}}
\date{}

\maketitle

\end{titlepage}
"""


def build_abstract(body: str) -> str:
    """概要はテンプレートに合わせて chapter* で組む。"""
    return ("\\chapter*{中間報告概要}\n"
            "\\addcontentsline{toc}{chapter}{中間報告概要}\n\n") + body


def patch_main(text: str) -> str:
    r"""テンプレートの main.tex に必要な変更を加える。

    本文の表で tabularx を、参考文献で url を使うため、パッケージを足す。
    それ以外はテンプレートのまま変えない。参考文献は
    reference/reference.tex に thebibliography 形式で書き出すので、
    テンプレートの \include をそのまま使える。
    """
    anchor = "\\usepackage{caption}"
    assert text.count(anchor) == 1, "main.tex の想定が違う"
    text = text.replace(
        anchor,
        anchor
        + "\n\\usepackage{tabularx}  % 本文の表で使用"
        + "\n\\usepackage{url}       % 参考文献の URL で使用",
    )
    text = text.replace(
        "% 2019年度　本論文　テンプレート",
        "% 2026年度 卒業研究 中間報告\n"
        "% 研究室テンプレートに interim-thesis の原稿を流し込んだもの。\n"
        "% 原稿を直す場合は interim-thesis/*.md を直し、\n"
        "% interim-thesis/md2tex.py を実行し直すこと。",
    )
    return text


def main() -> int:
    import shutil

    if OUT.exists():
        shutil.rmtree(OUT)
    for sub in ["", "figure", "abstract", "reference"] + [f"chapter{n}" for n in range(1, 8)]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    cites = load_citation_map()
    print(f"引用の対応: {len(cites)} 件")

    for src_name, out_name, title in CHAPTERS:
        body = convert(SRC / src_name, cites, title)
        if out_name.startswith("abstract"):
            body = build_abstract(body)
        (OUT / out_name).write_text(body, encoding="utf-8")
        print(f"  {src_name} -> {out_name}")

    (OUT / "reference" / "reference.tex").write_text(
        build_bibliography(), encoding="utf-8")
    print("  reference/reference.tex")

    (OUT / "title.tex").write_text(TITLE, encoding="utf-8")
    print("  title.tex")

    main_tex = (TEMPLATE / "main.tex").read_text(encoding="utf-8")
    (OUT / "main.tex").write_text(patch_main(main_tex), encoding="utf-8")
    shutil.copy(TEMPLATE / "latexmkrc", OUT / "latexmkrc")
    print("  main.tex / latexmkrc")

    figdir = SRC.parent / "research" / "experiment" / "pilot" / "figures_fixed"
    for _num, (dst, src_name, _w) in FIGURES.items():
        src_path = figdir / f"{src_name}.png"
        if src_path.exists():
            shutil.copy(src_path, OUT / "figure" / f"{dst}.png")
            print(f"  figure/{dst}.png")
        else:
            print(f"  [警告] 図が見つかりません: {src_path}")

    bib = SRC.parent / "research" / "references.bib"
    if bib.exists():
        shutil.copy(bib, OUT / "references.bib")
        print("  references.bib（BibTeX を使う場合のみ）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
