# Overleaf への取り込み手順

`interim-thesis/` の Markdown 原稿を `md2tex.py` で変換した LaTeX 一式．
原稿を直した場合は `python md2tex.py` を実行し直せば，このフォルダが
作り直される．**このフォルダの .tex を直接編集すると次の変換で消えるので，
直すときは Markdown 側を直すこと．**

2 段組みのテンプレートで組むことを前提にしている．

## ファイル

| ファイル | 内容 |
|---|---|
| `main.tex` | 単体でコンパイルできる本体（2 段組み）．テンプレートを使う場合は不要 |
| `abstract.tex` | 要旨 |
| `chapter1.tex` 〜 `chapter7.tex` | 第1章〜第7章 |
| `references.tex` | 参考文献（`thebibliography` 形式．**BibTeX 不要**） |
| `references.bib` | 参考文献（BibTeX 形式．使いたい場合のみ） |
| `figures/confidence-distribution.png` | 図 5.1 確信度の分布 |
| `figures/reliability-diagram.png` | 図 5.2 信頼度ダイアグラム |

## テンプレートに必要なパッケージ

**プリアンブルに以下が入っているか必ず確認すること．** 入っていないと
表が崩れるか，コンパイルが通らない．

```latex
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{tabularx}   % 幅の広い表の折り返しに必要
\usepackage{url}        % 参考文献の URL に必要
```

## 手順 A：研究室指定のテンプレートに入れる場合

1. `abstract.tex`，`chapter1.tex` 〜 `chapter7.tex`，`references.tex`，
   `figures/` をアップロードする．
2. 上記のパッケージがプリアンブルにあるか確認し，無ければ足す．
3. テンプレートの本体に以下を書く．

```latex
\input{chapter1}
\input{chapter2}
\input{chapter3}
\input{chapter4}
\input{chapter5}
\input{chapter6}
\input{chapter7}
\input{references}
```

要旨はテンプレートの abstract 環境の中で `\input{abstract}` とする．

## 手順 B：そのまま使う場合

フォルダ全体を Overleaf にアップロードし，Menu で

- Compiler を **LaTeX**（uplatex + dvipdfmx）
- Main document を `main.tex`

にする．`main.tex` のタイトルと著者名は仮置きなので確認すること．

## 参考文献について

**`references.tex`（`thebibliography` 形式）を使えば BibTeX の実行は不要**
である．`\input{references}` を本文の最後に置けば，1 回のコンパイルで
参考文献が出る．

BibTeX を使いたい場合は，`\input{references}` の代わりに

```latex
\bibliographystyle{junsrt}
\bibliography{references}
```

と書き，`references.bib` をアップロードする．この場合は Overleaf の
Recompile を 2 回以上実行する（1 回目だけでは引用が `[?]` のままになる）．

## 2 段組みへの対応

段の幅を超えないよう，以下の処理を入れている．

- **幅の広い表は `table*` で 2 段抜きにしている．** 11 個中 9 個が該当する．
- **長い文を含む列は `tabularx` の `X` 列**にして折り返している（表 3.3，3.4）．
  `l` 列は折り返さないため，そのままでは枠の外へ出る．
- **図 5.1（確信度の分布）は横長のため `figure*` で 2 段抜き**にしている．
  1 段に入れると潰れて読めない．
- **長いファイル名は区切り記号のあとで改行できる**ようにしている．

## 確認が要る箇所

コンパイルできる環境が手元に無いため，**組版の確認はしていない**．

- **`table*` と `figure*` の位置．** 2 段抜きの float はページ上部にしか
  置けないため，本文から離れた位置に出ることがある．離れすぎる場合は
  該当箇所を `[t]` から `[tp]` にするか，本文の順序を調整する．
- **表 5.1 は 9 列ある．** 2 段抜きにしても収まらない場合は，`\small` を
  `\footnotesize` にするか UNC 列を落とす．
- **第3章のプロンプト例は `verbatim`．** 日本語が等幅フォントで崩れる
  場合は `quote` 環境の通常段落に変える．

## 既知の制約

- `md2tex.py` はこの原稿専用であり，Markdown 一般を扱うものではない．
- 本文の句読点は「，．」のまま出力している．
- 見出しは `\section` から始まる（article 系テンプレート向け）．
  book 系に入れる場合は `md2tex.py` の `STYLE` を `"book"` にする．
