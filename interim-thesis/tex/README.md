# Overleaf への取り込み手順

`interim-thesis/` の Markdown 原稿を `md2tex.py` で変換した LaTeX 一式．
原稿を直した場合は `python md2tex.py` を実行し直せば，このフォルダが
作り直される．**このフォルダの .tex を直接編集すると次の変換で消えるので，
直すときは Markdown 側を直すこと．**

## ファイル

| ファイル | 内容 |
|---|---|
| `main.tex` | 単体でコンパイルできる本体．研究室指定のテンプレートを使う場合は不要 |
| `abstract.tex` | 要旨 |
| `chapter1.tex` 〜 `chapter7.tex` | 第1章〜第7章 |
| `references.bib` | 参考文献（`research/references.bib` の複製） |
| `figures/confidence-distribution.png` | 図 5.1 確信度の分布 |
| `figures/reliability-diagram.png` | 図 5.2 信頼度ダイアグラム |

## 手順 A：研究室指定のテンプレートに入れる場合

1. テンプレートのプロジェクトに，`abstract.tex`，`chapter1.tex` 〜
   `chapter7.tex`，`references.bib`，`figures/` をアップロードする．
2. テンプレートの本体に以下を書く．

```latex
\input{abstract}
\input{chapter1}
\input{chapter2}
\input{chapter3}
\input{chapter4}
\input{chapter5}
\input{chapter6}
\input{chapter7}
```

3. プリアンブルに以下が無ければ追加する．

```latex
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
```

4. 参考文献は `\bibliographystyle{junsrt}` と `\bibliography{references}`．

## 手順 B：そのまま使う場合

このフォルダ全体を Overleaf にアップロードし，

- Menu → Compiler を **LaTeX**（uplatex + dvipdfmx）にする
- Main document を `main.tex` にする

`main.tex` の著者名・タイトル・日付は仮置きなので確認すること．

## 変換結果

| 章 | 表 | 図 | 数式 | 引用 |
|---|---|---|---|---|
| 第1章 | 0 | 0 | 0 | 8 |
| 第2章 | 0 | 0 | 0 | 22 |
| 第3章 | 4 | 1 | 7 | 8 |
| 第4章 | 2 | 0 | 0 | 0 |
| 第5章 | 4 | 2 | 0 | 0 |
| 第6章 | 0 | 0 | 0 | 1 |
| 第7章 | 1 | 0 | 0 | 0 |

引用は本文の `[1]` 等を BibTeX キーに変換済み．25 キーすべてが
`references.bib` に存在することを確認している．

## 確認が要る箇所

コンパイルできる環境が手元に無いため，**組版の確認はしていない**．
以下は実際に組んでから調整すること．

- **表の幅．** 表 5.1 は 9 列あり，用紙幅に収まらない可能性がある．
  溢れる場合は `\small` を `\footnotesize` にするか，UNC 列を落とす．
  各表には `\small` を付けてある．
- **図 3.1．** 処理フローを枠付きの箱と矢印で組んである．そのまま使えるが，
  作図ソフトで清書したものに差し替えてもよい．差し替える場合は
  `chapter3.tex` の該当 figure を置き換える．
- **図の配置．** `[htbp]` を指定しているので，位置がずれる場合は調整する．
- **第4章のプロンプト例．** `verbatim` で出力している．日本語が等幅フォントで
  崩れる場合は `\begin{quote}` + 通常の段落に変える．

## 既知の制約

- `md2tex.py` はこの原稿専用であり，Markdown 一般を正しく扱うものではない．
- 本文の句読点は「，．」のまま出力している．
- 表は罫線をすべて引く形（`|l|l|...`）にしてある．研究室の慣行に合わせて
  `booktabs` の形に変える場合は手で直すこと．
