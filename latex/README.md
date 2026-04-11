# LaTeX 卒論テンプレート

## 前提

- **LuaLaTeX** を使用（日本語処理に `luatexja` を利用）
- 参考文献管理: **Biber** + `biblatex`（authoryear スタイル）

## ファイル構成

```
latex/
├── main.tex              # メインファイル（表紙・目次・章の読み込み）
├── references.bib        # 参考文献データベース（research/references.bib のコピー）
├── Makefile              # ビルド自動化
├── chapters/
│   ├── chapter1.tex      # 第1章 序論
│   ├── chapter2.tex      # 第2章 関連研究
│   ├── chapter3.tex      # 第3章 研究方法
│   ├── chapter4.tex      # 第4章 実験結果
│   ├── chapter5.tex      # 第5章 考察
│   └── chapter6.tex      # 第6章 結論
├── figures/              # 図（PDF/PNG）
└── appendices/           # 付録（必要に応じて）
```

## ビルド方法

```bash
cd latex
make          # PDF 生成（lualatex → biber → lualatex × 2）
make clean    # 中間ファイル削除
make watch    # ファイル変更を監視して自動ビルド（要 inotifywait）
```

## 注意事項

- `references.bib` を更新したら `research/references.bib` にも反映すること
  （将来的にはシンボリックリンクにしてもよい）
- 大学のフォーマット要件（余白・フォントサイズ等）は `main.tex` の `\geometry` で調整
- 提出前に `templates/submission-checklist.md` を確認すること

## 代替: pLaTeX を使う場合

大学の環境が pLaTeX を前提としている場合は `main.tex` の冒頭を:
```latex
\documentclass[12pt,a4paper,titlepage]{jsarticle}
\usepackage[dvipdfmx]{graphicx}
\usepackage[dvipdfmx]{hyperref}
```
に変更し、ビルドコマンドを `platex → dvipdfmx` に切り替える。
