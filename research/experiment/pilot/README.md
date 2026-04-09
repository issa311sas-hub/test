# パイロット実験 — 実行ガイド

> **テーマ**: LLMの自己評価能力検証（日本語）
> **目的**: 本実験の前に、小規模で方法論を検証する

---

## ディレクトリ構成

```
experiment/pilot/
├── README.md               # このファイル
├── requirements.txt        # Python依存パッケージ
├── questions_sample.csv    # 50問のサンプル問題データセット
├── prompts.py              # プロンプトテンプレート
├── parser.py               # 応答パーサー（回答・信頼度の抽出）
├── calibration.py          # ECE, Brier, AUROC の計算
├── run_pilot.py            # 実行スクリプト
└── results/                # 実行結果の保存先（実行時に作成される）
```

---

## セットアップ

### 1. Python環境
Python 3.10以上を推奨。

```bash
# 仮想環境を作る（推奨）
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt
```

### 2. APIキーの設定
各モデルのAPIキーを環境変数に設定する。

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
# Gemini: export GOOGLE_API_KEY="..."
```

**注意**: APIキーはGitリポジトリに絶対にコミットしないこと。`.gitignore`で除外される。

---

## 使い方

### Step 1: まず1問だけで動作確認

一番最初は、いきなり50問を全モデルで走らせるのではなく、**1〜5問だけ**で動作確認する。

```bash
python run_pilot.py \
  --model gpt-4o \
  --questions questions_sample.csv \
  --output results/gpt4o_test.csv \
  --limit 5
```

### Step 2: 2つ目のモデルで動作確認

```bash
python run_pilot.py \
  --model claude-sonnet-4-6 \
  --questions questions_sample.csv \
  --output results/claude_test.csv \
  --limit 5
```

### Step 3: 全50問を2モデルで実行

```bash
python run_pilot.py \
  --model gpt-4o \
  --questions questions_sample.csv \
  --output results/gpt4o_full.csv

python run_pilot.py \
  --model claude-sonnet-4-6 \
  --questions questions_sample.csv \
  --output results/claude_full.csv
```

### Step 4: 結果を分析

簡単な分析はJupyter Notebookで行う：

```python
import pandas as pd
import numpy as np
from calibration import compute_all

df_gpt = pd.read_csv("results/gpt4o_full.csv")
df_claude = pd.read_csv("results/claude_full.csv")

for name, df in [("GPT-4o", df_gpt), ("Claude", df_claude)]:
    valid = df[df["parse_success"] == 1]
    conf = valid["confidence"].astype(float).to_numpy()
    correct = valid["correct"].astype(int).to_numpy()
    metrics = compute_all(conf, correct)
    print(f"\n{name}:")
    print(f"  N = {metrics.n}")
    print(f"  Accuracy = {metrics.mean_accuracy:.2%}")
    print(f"  Mean Confidence = {metrics.mean_confidence:.2%}")
    print(f"  ECE = {metrics.ece:.4f}")
    print(f"  Brier = {metrics.brier:.4f}")
    print(f"  AUROC = {metrics.auroc:.4f}" if metrics.auroc else "  AUROC = N/A")
```

---

## チェックリスト（パイロット完走時）

- [ ] 両モデルで全50問が実行できた
- [ ] パースエラー率が10%以下
- [ ] ECE・Brier・AUROCが妥当な値で出力された
- [ ] API費用が想定内（目安500円以下）
- [ ] Reliability Diagramが描画できた
- [ ] ドメイン別（commonsense/math/history/translation）の集計ができた
- [ ] パイロットから本実験への改善点をまとめた

---

## コスト見積もり

| モデル | 単価目安 | 50問の費用 |
|---|---|---|
| GPT-4o | 約$0.0025/1k tok | 約50〜150円 |
| Claude Sonnet 4.6 | 約$0.003/1k tok | 約50〜150円 |
| **合計** | - | **約100〜300円** |

※ 実際のトークン数次第。大幅に超えないよう `--limit` で段階的に実行する。

---

## トラブルシューティング

### 1. パースエラー率が高い
- モデルが指定フォーマットを守らない → プロンプトを厳格化（`prompts.py`）
- 特定モデルだけ形式が違う → モデル別にプロンプトを用意

### 2. レート制限エラー
- `time.sleep(0.5)` の値を増やす
- バッチ処理に切り替える（将来の拡張）

### 3. API費用が想定より多い
- 問題数を減らす
- 長すぎる質問文を短縮する

### 4. 信頼度が極端（全部100や全部50）
- プロンプトで「多様な値を使うように」と明示する
- それでも変わらない場合、モデルの傾向として結果に記録

---

## 次のステップ（パイロット完走後）

1. `results/` の結果をもとに **パイロット報告書**（`pilot-report.md`）を書く
2. 指導教員に**パイロット結果を報告**
3. フィードバックをもとに**本実験の設計を修正**
4. 本実験では問題数200・モデル4〜6・条件3〜4に拡大

---

## 注意事項

- **APIキーを絶対にコミットしない**
- **プロンプトとモデルバージョンは必ず記録する**（再現性）
- **結果CSVは日時付きでバックアップ**を取る
- **人間の正解判定に主観が入る場合は、複数人でチェック**
