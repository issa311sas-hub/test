# 研究の論理監査（2026-07-13）

> 目的: `research/papers/` にある28本の論文（うち16本は本日確認）の内容を実際に精読し、
> 研究計画書・要旨・分析ドキュメントとの整合性を検証。筋が通っていない点・不確実な点を洗い出し、修正した。
> 修正方針: 各ステップの根拠論文を明示し、「なぜこの設計か」を一歩ずつ説明できる状態にする。

## 見つかった問題と対応

### 🔴 問題1: 「日本語での検証は存在しない」という新規性の主張が過大だった

**発見の経緯**: `MlingConf`（Xue et al. 2025, ACL Findings）を精読したところ、
英語・日本語・中国語・フランス語・タイ語の**5言語**で verbalized confidence を含む3手法
（Prob./p(True)/Verb.）を実際に検証しており、日本語もその対象に含まれていた。

**問題があった記述**:
- `research-proposal-draft.md` §2.2, §4.5「日本語環境での検証は存在しない」「日本語タスクでの初の体系的評価」
- `abstract_v1.tex` §1「日本語タスクにおいて同様のプロンプト設計が較正精度を改善するかは十分に検証されていない」
- `why-prompt-design-defense.md` Q2, Q3, §6「日本語での比較も空白」
- `user-action-checklist.md` Q&A想定問答「日本語での再現性は未検証」
- `theme-deep-dive.md`「日本語での先行研究はほぼ存在しない」
- `thesis-drafts/chapter1-introduction-draft.md`（自己レビューのメモ内）

**対応**: 上記すべてを、MlingConfの存在を前提とした精緻な主張に修正した。
新しい新規性の主張は以下の3点に限定:
1. MlingConfは単一のverbalized confidence手法のみ検証 → 本研究はVerb.1S/Verb.2S/Ling.1Sの**方式間比較**を行う
2. MlingConfは英語発の問題を機械翻訳 → 本研究はJCommonsenseQA・JMMLU等の**日本語ネイティブデータセット**を使う
3. MlingConfはGPT-3.5・Llama-3.1のみ → 本研究はGPT-4o・Claude・Gemini・Swallow等**新しい世代のモデル**を含む

**追加の発見（副産物）**: MlingConfの実測データ（Table 4, TriviaQA on GPT-3.5: 英語ECE=16.52 vs 日本語ECE=34.49等）が、
H4「日本語での改善幅は英語より小さい」という仮説の**実証的な裏付け**になることが分かった。
従来は「言語による確信度スケールの違い」という漠然とした理由だけだったが、具体的な先行データで補強した。

---

### 🔴 問題2: Jang et al. 2025 の引用が誤りだった

**発見の経緯**: `prompt-design-analysis.md` で「"Verbalized Confidence Triggers Self-Verification" (Jang et al. 2025) は
Verb.2Sの理論的裏付け」と記載されていたため、PDFを精読して検証した。

**判明した事実**: Jang et al. 2025 は **LoRAによるfine-tuning（CSFT）** でCoT推論に自己検証行動
（低確信度時に「もう一度計算し直す」等の言い直し）を誘発させる手法であり、
(1) fine-tuningを要する点、(2) 「自己検証」は confidence score そのものの較正精度ではなくCoTの推論過程の
振る舞いを指している点、の2点で本研究のVerb.2S（プロンプトのみ・別ターンで確信度を尋ねる）とは無関係だった。

**対応**: `prompt-design-analysis.md` から誤った引用を削除し、訂正メモを追加。
`missing-papers-checklist.md` の該当記述も訂正。Verb.2Sの理論的根拠はADVICE（Seo 2025）の
診断的知見（回答非依存性が過信の主因）のみに限定した。

---

### 🟡 問題3: `references.bib` に未登録の中核論文が5本あった

Xue 2025 (MlingConf)、Seo 2025 (ADVICE)、Dai 2025 (Rescaling Confidence)、
Yang 2024 (Verbalized Confidence Scores)、Li et al. 2025 (ConfTuner) は
すでにPDFがあり本文でも多用されているにもかかわらず、bibtexエントリが存在しなかった。
また Ferro & Fricker 2012（PDF未入手）も未登録だった。→ 全て追加した。

**副産物のミス**: ConfTuner のbibエントリを最初に追加した際、著者名を誤って
「Xiao, Hou, Wang, Jin, Long, Su, Shen」（別論文 Xiao et al. 2025「Restoring Calibration」の著者）
にしてしまっていた。PDF本文を再確認し、正しい著者「Li, Xiong, Wu, Hooi」に訂正した。

---

### 🟢 問題4: 引用番号の不整合（未修正・要注意）

`research-proposal-draft.md` §2.1-2.2 の本文中の `[1][2][3][4]` という角括弧引用番号が、
§11 の参考文献リストの通し番号（1.Guo 2.Kadavath 3.Lin 4.Tian 5.Xiong...）とズレている
（例: 本文は「Tian et al. 2023 [3]」だが、§11のリストではTianは4番目）。

**対応状況**: 未修正。これは草稿段階の表記ゆれであり、内容の論理性には影響しないため、
今回は優先度を下げた。**卒業論文の本執筆時には、BibTeXの `\cite{}` に置き換えて
自動採番することを推奨**（`references.bib` は既に整備済みなので、LaTeX執筆時に
`tian2023justask` のようなbibkeyで引用すれば自動的に解決する）。

---

## 修正したファイル一覧

| ファイル | 修正内容 |
|---|---|
| `research-proposal-draft.md` | §2.2-2.4 新規性主張の精緻化、§2.5「研究の論理的な繋がり」新設、§4.3/4.6 MlingConfとの違いを明記、H4の根拠を実測値で補強 |
| `midterm-presentation/abstract/abstract_v1.tex` | §1 新規性主張を精緻化、MlingConf引用を追加 |
| `why-prompt-design-defense.md` | Q2/Q3/§5/§6 の過大な新規性主張を訂正、MlingConf参照を追加 |
| `prompt-design-analysis.md` | Jang 2025の誤引用を削除・訂正メモ追加、ADVICEの位置づけを明確化 |
| `user-action-checklist.md` | Q&A想定問答の「日本語検証未実施」を訂正 |
| `theme-deep-dive.md` | 「日本語の先行研究ほぼ存在しない」に訂正メモ追加 |
| `thesis-drafts/chapter1-introduction-draft.md` | 自己レビューメモに訂正注記追加 |
| `dataset-selection-analysis.md` | MlingConfのarXiv番号が未確認だった点を訂正（PDFで確認済み情報に置換） |
| `answer-judgment-analysis.md` | Shi et al. の著者名・年・会議を訂正（前回セッションで実施） |
| `references.bib` | 未登録6論文の追加、ConfTuner著者名の誤りを訂正 |
| `missing-papers-checklist.md` | Jang 2025の位置づけ訂正 |

## 「一歩ずつ論理をつなげる」ための追加

`research-proposal-draft.md` §2.5 に、Guo 2017（ECE基礎）→ Kadavath/Lin（自己評価の可能性）→
Tian/Xiong（英語での有効性）→ MlingConf（多言語だが粗い検証）→ Xia 2025（プロンプトスタイル依存性）→
Dai 2025（スケール設計）→ ADVICE（回答接地）→ Black-Box Survey（プロンプト以外が使えない理由）→
**本研究の位置**、という10段階の論理チェーンを表形式で追加した。
指導教員・審査委員から「なぜこの設計か」を問われた際、この表の各行を辿ることで
一歩ずつ説明できる構成にした。
