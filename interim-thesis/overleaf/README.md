# Overleaf にそのままインポートできる一式

研究室のテンプレート（`jreport`・1 段組み）に，`interim-thesis/` の原稿を
流し込んだもの．**この一式を zip にして Overleaf にアップロードすれば，
そのままコンパイルできる．**

**この一式は実際にコンパイルして検証してある**（platex + dvipdfmx，
latexmk 4 パス）．結果は 57 ページ，エラー 0 件，未解決の引用 0 件．

## Overleaf での操作

1. New Project → Upload Project → zip を選ぶ
2. Menu を開き，**Compiler** が `LaTeX`，**Main document** が `main.tex`
   になっているか確認する
3. Recompile

参考文献は `thebibliography` 形式なので，**BibTeX の実行は不要**．

## 構成

| ファイル | 内容 |
|---|---|
| `main.tex` | 本体（テンプレートに 2 行追加） |
| `latexmkrc` | コンパイル設定（テンプレートのまま） |
| `title.tex` | 表紙 |
| `abstract.tex` | 中間報告概要 |
| `chapter1.tex` 〜 `chapter7.tex` | 第1章〜第7章 |
| `reference.tex` | 参考文献（25 件） |
| `figure/` | 図 5.1・5.2 |
| `references.bib` | BibTeX 版（使う場合のみ） |

## 章をフォルダに分けていない理由

テンプレートは `chapter1/index1.tex` のようにフォルダを分け，`\include` で
読み込んでいる．**この形は Overleaf で失敗した．**

`\include` はファイルごとに `.aux` を書くため，対応するフォルダが無いと

```
! I can't write on file `chapter4/index4.aux'.
! Emergency stop.
```

で停止する．実際にこの症状が出て，**第 4 章以降と参考文献が出力されず，
全 28 ページで打ち切られた**．手元で同じ状況を再現し，ページ数・
未解決引用の数まで一致することを確認した．

そこで章をフォルダに分けず，`\input` で読み込む形に変えた．`\input` は
`.aux` を書かないため，この失敗は起きない．`main.tex` の該当行は
`\include{chapter1/index1}` から `\input{chapter1}` に書き換えてある．

## テンプレートへの変更

`main.tex` への変更は以下だけ．組版に関わる設定は一切変えていない．

```latex
\usepackage{tabularx}  % 本文の表で使用
\usepackage{url}       % 参考文献の URL で使用
```

加えて，上記の理由で `\include{chapterN/indexN}` を `\input{chapterN}` に，
`\include{abstract/abstract}` を `\input{abstract}` に，
`\include{reference/reference}` を `\input{reference}` に書き換えている．

## 表紙

`title.tex` の内容を確認すること．

- 2026年度 卒業研究 中間報告
- 東京理科大学 創域理工学部 経営システム工学科 秦野研究室
- 7422048 指田 一茶／指導教員 秦野 亮

## 本文幅への対応

- 長い文を含む列がある表（3.3，3.4，4.1，4.2，7.1）は `tabularx` の `X` 列で
  折り返す．`l` 列は折り返さないため，そのままでは本文幅を超える．
- 列数が多い表 5.1（9 列）は，テンプレートの流儀に合わせて `\scalebox` で
  縮めている．本文幅に収まることを組版して確認済み．
- 長いファイル名は区切り記号のあとで改行できるようにしている．

## 既知の残件

- **表紙で 12pt（約 4mm）のはみ出しが 1 箇所出る．** テンプレートの
  `\center{}` と `\rightline{}` の書き方に由来するもので，タイトルが
  中央揃えのため見た目にはほぼ分からない．テンプレート付属の見本でも
  同じ警告が出る．気になる場合はタイトルを 3 行に分ける．
- **図 3.1（評価の処理フロー）** は枠と矢印で組んであり，そのまま使えるが，
  作図ソフトで清書したものに差し替えてもよい．

## 原稿を直す場合

**このフォルダの `.tex` を直接編集しないこと．** 次に変換したとき消える．

原稿は `interim-thesis/*.md` にある．直したあと，

```
cd interim-thesis
python md2tex.py
```

を実行すると，このフォルダが作り直される．Overleaf 側で最終的な微調整を
する分には，直接編集してかまわない．
