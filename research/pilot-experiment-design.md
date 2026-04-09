# パイロット実験 設計書

> **作成日**: 2026年4月9日
> **目的**: 本実験の前に、50問×1〜2モデルで小規模に方法論を検証する
> **実施予定**: 2026年5月

---

## 1. パイロット実験の目的

本実験を始める前に、以下を検証する：

1. **プロンプトが期待通り動くか**（モデルが確信度を数値で返すか）
2. **確信度のパース（抽出）**が自動化できるか
3. **ECE・Brier Score**の計算スクリプトが正しく動くか
4. **API費用の実測**（本実験のコスト見積もりの精度向上）
5. **1問あたりのAPIレスポンス時間**
6. **エラー処理**（タイムアウト、レート制限、フォーマットずれ）

---

## 2. パイロット実験のスコープ（小さく）

| 項目 | パイロット | 本実験 |
|---|---|---|
| 問題数 | 50問（常識10＋数学10＋歴史10＋翻訳10＋予備10） | 200問 |
| モデル数 | 2モデル（GPT-4o or GPT-5, Claude Sonnet 4.6） | 4〜6モデル |
| プロンプト条件 | 1条件（基本形のみ） | 3〜4条件 |
| 言語 | 日本語のみ | 日本語＋英語 |

→ コールの総数: 50問 × 2モデル × 1条件 = 100コール
→ 予想コスト: 100〜500円程度

---

## 3. データセット（パイロット用50問の内訳）

### 3.1 常識ドメイン（10問）
- 出典: JCommonsenseQA から抜粋
- 例: 「りんごを食べる時、普通は何で切りますか？ A: 包丁 / B: のこぎり / C: ハサミ / D: 金槌」
- 正解ラベル: 選択肢記号

### 3.2 数学ドメイン（10問）
- 出典: 中学数学の文章題（自作＋教科書参考）
- 例: 「ある店でりんご3個で600円、みかん5個で500円です。りんご1個とみかん1個を合計いくらで買えますか？」
- 正解ラベル: 数値

### 3.3 歴史ドメイン（10問）
- 出典: 高校日本史の事実質問
- 例: 「鎌倉幕府が開かれたのは西暦何年ですか？」
- 正解ラベル: 年号または語句

### 3.4 翻訳ドメイン（10問）
- 出典: 日英短文対訳（自作 or Floresから抜粋）
- 例: 「『私は明日図書館に行きます』を英語に訳してください」
- 評価: BLEU or 人手判定（Yes/No）

### 3.5 予備問題（10問）
- 各ドメインの難問・境界ケースを含む

---

## 4. プロンプトテンプレート（パイロット版）

```text
あなたは質問に回答するアシスタントです。
以下の問題に回答した後、自分の回答が正しい確率を0〜100の整数で表してください。

問題:
{question}

選択肢（ある場合）:
{choices}

以下の形式で、必ずこの通りに出力してください：

回答: <ここに回答>
信頼度: <0〜100の整数>

他の余計な文章は出力しないでください。
```

---

## 5. 実装計画

### 5.1 ディレクトリ構造（仮）
```
research/
├── experiment/
│   ├── pilot/
│   │   ├── questions.csv        # 50問のデータセット
│   │   ├── prompts.py           # プロンプトテンプレート
│   │   ├── run_pilot.py         # 実行スクリプト
│   │   ├── calibration.py       # ECE/Brier計算
│   │   ├── results/
│   │   │   ├── gpt4o_raw.csv
│   │   │   ├── claude_raw.csv
│   │   │   └── analysis.ipynb
│   │   └── logs/
```

### 5.2 データフォーマット（questions.csv）
```csv
id,domain,question,choices,correct_answer,answer_type
1,commonsense,"りんごを食べる時に使うものは？","包丁|のこぎり|ハサミ|金槌",包丁,mc
2,math,"りんご3個600円、みかん5個500円。りんご1個とみかん1個の合計は？",,300,numeric
...
```

### 5.3 疑似コード（run_pilot.py）
```python
import pandas as pd
from openai import OpenAI
from anthropic import Anthropic

def build_prompt(row):
    template = open("prompts/basic.txt").read()
    return template.format(
        question=row["question"],
        choices=row.get("choices", "（選択肢なし）")
    )

def parse_response(text):
    # 「回答:」「信頼度:」を抽出
    answer = ...
    confidence = ...
    return answer, confidence

def run_model(model_name, questions):
    results = []
    for _, row in questions.iterrows():
        prompt = build_prompt(row)
        response = call_api(model_name, prompt)
        answer, confidence = parse_response(response)
        correct = judge(answer, row["correct_answer"])
        results.append({
            "id": row["id"],
            "model": model_name,
            "answer": answer,
            "confidence": confidence,
            "correct": correct
        })
    return pd.DataFrame(results)

questions = pd.read_csv("questions.csv")
df_gpt = run_model("gpt-4o", questions)
df_claude = run_model("claude-sonnet-4-6", questions)
df_all = pd.concat([df_gpt, df_claude])
df_all.to_csv("results/pilot_raw.csv", index=False)
```

### 5.4 calibration.py の疑似コード
```python
import numpy as np

def compute_ece(confidences, correct, n_bins=10):
    """Expected Calibration Error"""
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (confidences >= lo) & (confidences < hi)
        if mask.sum() > 0:
            avg_conf = confidences[mask].mean()
            avg_acc = correct[mask].mean()
            ece += (mask.sum() / len(confidences)) * abs(avg_conf - avg_acc)
    return ece

def compute_brier(confidences, correct):
    return np.mean((confidences - correct) ** 2)
```

---

## 6. 期待される成果（パイロット）

### 定量的アウトプット
- `pilot_raw.csv` ... 全モデル・全問題の生データ
- `calibration_metrics.csv` ... モデル別・ドメイン別のECE・Brier
- `reliability_diagram.png` ... 視覚化

### 定性的な学び
- プロンプトがうまく動かないケース（例: 信頼度を「自信あり」のような自然言語で返す）
- モデルによる応答スタイルの違い
- 自動パース失敗率

---

## 7. パイロット実験のスケジュール

| 日 | タスク |
|---|---|
| Day 1 | 問題データセットの準備（50問） |
| Day 2 | スクリプト実装（プロンプト+パース） |
| Day 3 | 小規模テスト（5問で動作確認） |
| Day 4 | 全50問を2モデルで実行 |
| Day 5 | 正誤判定・データクリーニング |
| Day 6 | ECE・Brier計算、可視化 |
| Day 7 | 結果のまとめ、本実験への反映事項の整理 |

**所要時間**: 約1週間（実働20〜30時間）
**実施月**: 2026年5月

---

## 8. パイロット実験で検証すべきチェックリスト

- [ ] 全モデルから想定フォーマットで応答が返ってくる
- [ ] 信頼度のパース成功率が90%以上
- [ ] 失敗時のリトライ処理が機能する
- [ ] API費用が想定内（目安: 500円以下）
- [ ] ECE計算結果が妥当な値（0.0〜0.5の範囲）
- [ ] Reliability Diagramが正しく描画される
- [ ] ドメイン間で明らかな差が見えるか・見えないか

これらの結果をもとに、本実験の設計を微調整する。

---

## 9. 本実験への反映事項（事前に想定）

パイロットの結果次第で、以下を調整する：
- 問題数の増減
- モデルの追加／削除
- プロンプト条件の絞り込み
- ドメインの再構成

---

## 10. 備考

- **最小動作確認**: まずはたった1問・1モデルで、エンドツーエンドの流れを通すことが最優先
- **アンチパターン**: いきなり200問やろうとしない。小さく早く失敗する
- **バージョン管理**: 結果CSVは日時とモデルバージョンをファイル名に含める
