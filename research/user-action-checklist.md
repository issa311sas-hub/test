# ユーザー実行手順書

> **作成日**: 2026-06-27  
> **対象**: Claude では実行できない、本人が必ず行う必要があるタスク  
> **最重要締切**: 2026-07-17（金）12:00 LETUS への概要 PDF 提出

---

## 🔴 締切順アクション一覧

| 期限 | タスク | 所要時間 | 詳細セクション |
|---|---|---|---|
| **7/17 12:00** | 概要 2p を PDF にして LETUS 提出 | 2〜3 時間 | §1 |
| 7/16 12:00 | 発表日程が他と重なる場合、教務幹事に連絡 | 15 分 | §2 |
| 7/中旬 | パイロット実験を手元で実行（API キーが必要） | 1 時間 | §3 |
| 7/20〜27 | 中間発表本番（6分＋質疑3分） | 3 時間 | §4 |

---

## §1 概要 2p の仕上げと PDF 提出（最優先）

### 1-1. LaTeX ファイルの確認

ドラフトは以下に作成済み：
```
research/midterm-presentation/abstract/abstract_v0.tex
```

**本人がやること：**
1. ファイルを開いて通読し、自分の言葉でない箇所を書き直す
2. 特に「研究の背景と動機」「今後の計画」は自分の文章に修正する
3. 先生に見てもらえる場合は 7/10 までにレビュー依頼（返答がなくても進める）
4. 修正後に `abstract_v1.tex` として保存

**コンパイル方法（PDF 生成）：**
```bash
# LuaLaTeX の場合
cd research/midterm-presentation/abstract/
lualatex abstract_v1.tex
# → abstract_v1.pdf が生成される

# upLaTeX の場合
uplatex abstract_v1.tex && dvipdfmx abstract_v1.dvi

# overleaf を使う場合
# ファイルをアップロードして「Compile」を押す
```

> **注意**: 日本語部分は `\usepackage{luatexja}` のコメントを外すか、
> Overleaf を使う（日本語 LaTeX 環境が整っている）。

### 1-2. LETUS への提出

1. LETUS にログイン
2. 「卒業研究1 中間発表概要」の提出フォームを探す
3. `abstract_final.pdf` をアップロード
4. **2026-07-17（金）12:00 厳守**

---

## §2 中間発表の日程調整（7/16 12:00 まで）

発表会は 7/20〜7/27 のどこか。グループ別に割り当てられる。

**もし他の予定と重なる場合：**
- 7/16（木）12:00 までに教務幹事に日程交換を申し出る
- 連絡が遅れると自動的にそのまま確定する

---

## §3 パイロット実験の実行（7月中旬）

実験スクリプトは整備済み。API キーを設定して実行するだけ。

### 3-1. 環境セットアップ

```bash
cd research/experiment/pilot/
pip install anthropic openai numpy

# API キーを環境変数に設定（.env ファイルは作らず、毎回手動 or ~/.bashrc）
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

### 3-2. 動作確認（5問だけ、コスト：数円）

```bash
# まず Claude で Verb.1S を 5 問だけテスト
python run_pilot.py \
  --model claude-sonnet-4-6 \
  --method verb_1s \
  --questions questions_sample.csv \
  --output results/test_verb1s.csv \
  --limit 5
```

**確認すること：**
- `results/test_verb1s.csv` が生成されているか
- Parse success が 5/5 になっているか
- `results/test_verb1s_summary.json` に ECE・REL・RES が出力されているか

### 3-3. 動作確認後のコマンド（全 3 方式）

```bash
# Verb.2S（2 ターン構成）
python run_pilot.py --model claude-sonnet-4-6 --method verb_2s \
  --questions questions_sample.csv --output results/test_verb2s.csv --limit 5

# Ling.1S（言語表現）
python run_pilot.py --model claude-sonnet-4-6 --method ling_1s \
  --questions questions_sample.csv --output results/test_ling1s.csv --limit 5
```

### 3-4. パイロット本番（250 問）

問題が発生していなければ、`questions_100.csv`（既存）から始める。

```bash
python run_pilot.py --model claude-sonnet-4-6 --method verb_1s \
  --questions questions_100.csv --output results/pilot_claude_verb1s.csv
```

コスト目安：100 問 × claude-sonnet-4-6 ≈ 約 $0.10〜0.20

---

## §4 中間発表本番（7/20〜27）

### 発表スライドについて

現在 `research/presentations/2026-06-24-seminar-slides-PRESENTED.pptx` が最新版。
中間発表用には内容の追加・更新が必要（Murphy 分解の追加、Q&A 対策の強化）。

**必要な追加スライド：**
1. 「なぜプロンプト設計か」（3 カテゴリ比較の図）← `why-prompt-design-defense.md` をもとに
2. Murphy 分解の説明（BS = REL − RES + UNC の直感的説明）
3. 仮説 H1〜H4 の一覧

スライド更新は Claude に頼めます（「中間発表用にスライドを更新して」と依頼）。

### 質疑応答対策

よく聞かれる質問と回答（詳細は `midterm-presentation-plan.md` §6 参照）：

| 質問 | 一言回答 |
|---|---|
| Murphy 分解を使う先行研究がないのはなぜ？ | 知られていなかった、というのが本研究の動機 |
| 250 問で統計的に十分か？ | 各ビン 25 問確保。先行研究と同水準 |
| Post-hoc 法と比べてなぜプロンプト設計？ | 商用 API では logits が非公開。プロンプトのみが唯一の選択肢 |
| 日本語特化の理由は？ | Tian 2023 が英語のみ。日本語での再現性は未検証 |

---

## §5 Claude が担当を継続するタスク

以下は Claude がいつでも対応できます。依頼するだけで OK：

- 実験スクリプトのバグ修正・機能追加
- 中間発表スライドの更新（`generate_slides.py` を修正）
- 実験結果（CSV）が手に入ったら ECE/REL/RES の分析と可視化
- 卒業論文の章別ドラフト作成（10 月〜）
- 参考文献の整理・BibTeX 更新

---

## ファイル構成（現在）

```
research/
├── research-proposal-draft.md    ← 研究計画書（最新: Murphy 分解確定採用版）
├── why-prompt-design-defense.md  ← 「なぜプロンプト設計か」防御論理
├── brier-score-murphy-decomposition-survey.md  ← 横断調査
├── midterm-presentation/
│   └── abstract/
│       └── abstract_v0.tex       ← 概要 2p ドラフト（★本人が推敲する）
└── experiment/pilot/
    ├── calibration.py            ← ECE / Brier / AUROC + Murphy 分解
    ├── prompts.py                ← Verb.1S / Verb.2S / Ling.1S テンプレート
    ├── run_pilot.py              ← 実験実行スクリプト（API キー設定後に使用）
    └── questions_sample.csv      ← サンプル問題（動作確認用）
```
