# 「なぜプロンプト設計か」防御論理ドキュメント

> **作成日**: 2026-06-24  
> **目的**: 先生・審査委員から「キャリブレーション改善手法は他にもあるのでは？」と問われたときの防御論理を整理する  
> **対応するゼミコメント**: 2026-06-24 指摘①

---

## 1. キャリブレーション改善手法の全体マップ

LLM のキャリブレーション改善手法は大きく **3 カテゴリ** に分類できる。

### カテゴリ A：Post-hoc Calibration（訓練後の事後調整）

| 手法 | 概要 | 代表論文 |
|---|---|---|
| Temperature Scaling | softmax 出力全体を定数 T でスケーリング | Guo et al. (2017, ICML) |
| Adaptive Temperature Scaling (ATS) | トークンごとに異なる T を予測 | arXiv:2409.19817 (EMNLP 2024) |
| Platt Scaling | ロジスティック回帰で確率を補正 | — |
| Isotonic Regression | 単調変換で較正曲線を修正 | — |
| Prior Adaptation | 事前分布を用いた教師なし較正 | arXiv:2307.06713 |

**根本的制約**: これらは **モデルの内部確率（logits）へのアクセスが前提**。  
GPT-4o、Claude 3.x/4.x、Gemini 等の商用 API では logits は原則非公開 → **API 利用者には適用不可**。

---

### カテゴリ B：Fine-tuning / Training-based（訓練ベース）

| 手法 | 概要 | 代表論文 |
|---|---|---|
| SFT for confidence expression | 確信度を言葉で表現するよう instruction tuning | Tian 2023 の拡張版 |
| Calibration-Aware RL (DPO/PPO) | 較正誤差を報酬関数に組み込んで強化学習 | arXiv:2601.13284 (2025) |
| Calibration-Aware Fine-Tuning | RLHF 後の較正崩れを SFT で修復 | arXiv:2505.01997 (2025) |
| Bayesian LoRA | LoRA アダプタにベイズ推論を組み合わせ | — |

**根本的制約**: **モデルパラメータへの書き込み権限（学習環境）が必要**。  
→ 商用 API では実行不可能。OSS モデル（Llama, Swallow 等）のみ対象。  
→ 計算コスト大（GPU 時間・費用）、専門的インフラが必要。

---

### カテゴリ C：Prompt-based / Black-box（プロンプトベース）

| 手法 | 概要 | 代表論文 |
|---|---|---|
| Verbalized Confidence | 「確信度は〇〇%」と言語で確信度を出力させる | **Tian 2023** (EMNLP), Xiong 2024 (ICLR) |
| 2-Stage Elicitation | 回答後に別ターンで確信度を質問 | Tian 2023 |
| Linguistic Expression | 「ほぼ確実」等の言語表現→数値マッピング | Tian 2023 |
| Self-Consistency Sampling | 複数回生成の一致率を確信度の代理指標に | Wang 2023 |
| Chain-of-Thought variants | CoT で推論過程を経由させて確信度を推定 | 各種 |

**利点**: API のみで実現可能。追加学習・logits アクセス一切不要。  
**注意**: CoT は確信度精度に**寄与しない**という実験結果が Tian 2023 で示されている。

---

## 2. なぜ本研究はプロンプト設計を選ぶのか（3 本の柱）

### 柱①：適用可能性（最も強い論拠）

```
商用 API（GPT-4o / Claude / Gemini）を対象とする研究では
Post-hoc も Fine-tuning も実行不可能。
プロンプト設計が唯一適用できる手法カテゴリである。
```

調査を裏付ける論文として「A Survey of Calibration Process for Black-Box LLMs」（arXiv:2412.12767, 2024年12月）が存在し、**black-box API 環境でのキャリブレーション手法は専用サーベイが必要なほど独立した研究領域**であることが示されている。

> **一言で言えば**: "ポストホック法や fine-tuning を使えない状況（= 現実のほとんどの API 利用者）"でも使えるのがプロンプト設計である。

---

### 柱②：コスト優位性（実用的論拠）

| 手法 | 必要リソース | 追加コスト |
|---|---|---|
| Temperature Scaling | logits + キャリブレーション用検証データ | GPU 不要だが logits アクセス必要 |
| Fine-tuning | GPU（数 〜 数十時間） + データ | 数千〜数十万円 |
| **プロンプト設計** | **API 呼び出し（1〜2 回）** | **本研究全体で約 $20** |

プロンプト設計は**ゼロコストの実装変更**で較正性能の改善を試みる唯一のアプローチ。  
→ 個人・中小企業・研究者が今すぐ適用できる実用的価値がある。

---

### 柱③：先行研究の空白（学術的論拠）

Tian 2023・Xiong 2024 は**英語環境のみ**で検証。日本語でのプロンプト設計によるキャリブレーション研究は現時点で確認できない。

さらに「Influences on LLM Calibration: A Study of Response Agreement, Loss Functions, and **Prompt Styles**」（arXiv:2501.03991, 2025）のように、プロンプトスタイルがキャリブレーションに与える影響を体系的に調べる方向性は 2025 年現在も活発に研究されており、**分野の中心課題**である。

---

## 3. 反論への対応

### Q1「Fine-tuning のほうが効果が高いのでは？」

> A: Fine-tuning の較正改善効果は確かに報告されているが（例: Calibration-Aware Fine-Tuning）、**商用 API を使う一般利用者にとっては選択肢にならない**。本研究のスコープは「現実の API 利用者が今すぐ適用できる手法」であり、fine-tuning との比較は研究の対象外。

### Q2「Self-Consistency のほうがよいのでは？」

> A: Self-consistency は複数回サンプリング（n=10〜40 など）を必要とし、**API コストが 10〜40 倍に増大する**。本研究が目指す「低コストで実用的な改善」の趣旨と相反する。また verbalized confidence との直接比較は Tian 2023 では実施されておらず、日本語環境での比較も空白。

### Q3「プロンプト設計で得られる改善は小さいのでは？」

> A: Tian 2023 では内部確率と比べ ECE が約 50% 削減されることが英語環境で確認されている。本研究はこれを日本語で再検証し、かつ確信度表現方式（Verb.1S / Verb.2S / Ling.1S）の間でどれが最良かを初めて日本語タスクで定量的に示す点が新規性。

---

## 4. 手法選択の意思決定ロジック（図解）

```
LLM のキャリブレーション改善を目指す
         │
         ▼
  モデルパラメータへのアクセスは？
   ├─ あり（OSS モデル）→ Fine-tuning / Post-hoc が選択肢に入る
   └─ なし（商用 API）→ プロンプト設計のみが選択肢
                    ↓
          本研究のターゲット環境
          GPT-4o / Claude / Gemini 等
```

---

## 5. 関連文献まとめ

| 論文 | 内容 | 本研究との関係 |
|---|---|---|
| Guo et al. (2017, ICML) | Temperature Scaling 提案 | Post-hoc の代表（本研究では使用不可） |
| Tian et al. (2023, EMNLP) | Verbalized confidence が内部確率より優秀 | 本研究の直接の先行研究 |
| Xiong et al. (2024, ICLR) | 複数モデルで Tian 2023 を再確認 | 先行研究補強 |
| arXiv:2409.19817 (EMNLP 2024) | Adaptive Temperature Scaling | Post-hoc の最新手法（本研究では適用不可） |
| arXiv:2412.12767 (2024) | **Black-box LLM 較正サーベイ** | 「プロンプトが唯一の手法」を支持する横断サーベイ |
| arXiv:2501.03991 (2025) | プロンプトスタイルとキャリブレーションの関係 | 本研究の位置づけを支持 |
| arXiv:2505.01997 (2025) | Calibration-Aware Fine-Tuning | Fine-tuning 手法の代表（本研究では適用不可） |

---

## 6. ゼミ発表用 1 スライドの論点案

**タイトル**: 「なぜプロンプト設計を選んだか」

1. キャリブレーション改善手法は 3 カテゴリ存在する（Post-hoc / Fine-tuning / Prompt-based）
2. **Post-hoc・Fine-tuning は logits またはパラメータへのアクセスが必須** → 商用 API 不可
3. Prompt-based のみが「API だけで今すぐ使える」唯一のカテゴリ
4. Tian 2023 が英語で有効性を示した → 日本語での検証が本研究の空白を埋める

---

## 補足：調査で発見したプロンプト設計関連の 2025 年新論文

- **arXiv:2603.17839「How do LLMs Compute Verbal Confidence?」(2026)**: 言語的確信度が後付け再構成ではなく自動的な自己評価であることを示す → 本研究の「言語化された確信度」の学術的正当性を支持
- **arXiv:2604.23333「Process Supervision of Confidence Margin」(2026)**: 確信度マージンの監視で較正を改善 → プロンプト設計の延長線上の研究
- **arXiv:2506.00072「Evaluating Prompt Engineering Techniques for Accuracy」(2025)**: プロンプトエンジニアリングと精度の関係を実験的に評価 → 本研究の方向性と一致
