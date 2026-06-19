# プロンプト設計分析：確信度引き出しプロンプトの設計根拠

> **作成日**: 2026-06-19
> **目的**: LLMから回答と確信度を同時に正しく出力させるプロンプト条件の整理・設計
> **関連**: `research-proposal-draft.md` §5.4

---

## 1. 先行研究のプロンプト手法一覧

### 1.1 Tian et al. 2023 (EMNLP) — "Just Ask for Calibration"

確信度引き出しの基盤的研究。RLHF-LM（ChatGPT, GPT-4, Claude）において、verbalized confidence が条件付き確率より ECE を相対的に約50%改善することを示した。

3つの戦略を提案:

| 戦略 | 概要 | 特徴 |
|---|---|---|
| **Top-K + Confidence** | K個の候補回答を確信度付きで生成、最高スコアを選択 | 候補比較により calibration 改善 |
| **Two-Stage** | Turn 1で回答、Turn 2で確信度を別途質問 | 回答と確信度評価の認知プロセスを分離 |
| **Linguistic** | 数値ではなく言語表現（高い/中程度/低い）で確信度表現 | 数値への変換マッピングが必要 |

**重要知見**: Top-K候補を先に出してから確信度を述べさせると、calibration がさらに改善される。これは「代替案の検討」が過信を抑制するためと解釈されている。

### 1.2 Xiong et al. 2024 (ICLR) — "Can LLMs Express Their Uncertainty?"

体系的フレームワーク: プロンプト戦略 × サンプリング × 集約 の3軸で整理。

5つのプロンプト戦略を提案・評価（GitHubリポジトリからプロンプトテンプレート取得済み）:

#### (A) Vanilla — 直接的な確信度要求
```
Read the question, provide your answer and your confidence in this answer.
Note: The confidence indicates how likely you think your answer is true.
Use the following format to answer:
Answer and Confidence (0-100): [ONLY the {answer_type}; not a complete sentence],
[Your confidence level, please only include the numerical number in the range of 0-100]%
Only the answer and confidence, don't give me the explanation.
```

#### (B) Chain-of-Thought (CoT) — 段階的推論 + 確信度
```
Read the question, analyze step by step, provide your answer and your confidence
in this answer. Note: The confidence indicates how likely you think your answer is true.
Use the following format to answer:
Explanation: [insert step-by-step analysis here]
Answer and Confidence (0-100): [ONLY the {answer_type}; not a complete sentence],
[Your confidence level, please only include the numerical number in the range of 0-100]%
Only give me the reply according to this format, don't give me any other words.
```

#### (C) Top-K — K個の候補 + 各確率
```
Provide your {k} best guesses and the probability that each is correct (0% to 100%)
for the following question. Give ONLY the {task_output_description} of your guesses
and probabilities, no other words or explanation.
```

#### (D) Self-Probing — 二段階の自己評価
```
[Stage 1: 通常回答を取得]
[Stage 2:]
Question: {question_text}
Possible Answer: {answer}
Q: How likely is the above answer to be correct? Please first show your reasoning
concisely and then answer with the following format:
Confidence: [the probability of answer {answer} to be correct, not the one you
think correct, please only include the numerical number]%
```

#### (E) Multi-Step — 段階的難易度
ラベル → 確信度 → 確率分布と段階を踏む。

**主要知見**:
- LLMは確信度を言語化する際に**体系的に過信**する
- Consistency-based 手法 > Vanilla verbalized（20ケース中13でハイブリッドが最良）
- Human-inspired 戦略は過信を軽減するが、GPT-4では効果が逓減
- CoTは推論の一貫性を高めるが、それが**より高い確信度報告**につながる（必ずしもcalibration改善ではない）

### 1.3 Yang et al. 2024 (arXiv:2412.14737) — "On Verbalized Confidence Scores"

複数のプロンプト変種を体系的に比較した研究。

**主要知見**:
- プロンプトの**聞き方**が確信度の信頼性に大きく影響
- 小規模LLMはシンプルなプロンプト表現が有効
- 大規模LLMはより複雑な手法でも対応可能
- 同じモデルでもプロンプト表現を変えるだけでECEが大幅に変動

### 1.4 Dai 2025 (arXiv:2603.09309) — "Rescaling Confidence"

確信度**スケール設計**に特化した研究。

**実験設計**: 6つのLLM × 3データセットでスケールを体系的に操作。

| スケール | meta-d'（メタ認知効率） | 特徴 |
|---|---|---|
| 0–100（標準） | ベースライン | 78%以上の回答が3つのラウンドナンバーに集中 |
| **0–20** | **一貫して改善** | 粒度の低下がメタ認知効率を向上 |
| 境界圧縮スケール | 悪化 | 範囲の歪みが悪影響 |
| 不規則範囲 | 改善せず | ラウンドナンバー選好は持続 |

**重要知見**:
- 0–100スケールでの**ラウンドナンバー問題**: 回答の78%以上が端数なしの値（例: 70, 80, 90）に集中
- 0–20スケールが meta-d' で一貫してベスト
- スケール設計は「第一級の実験変数」として扱うべき

**本研究への示唆**: 0–100スケールを使用する場合、ラウンドナンバー集中の分析を追加すべき。ただし先行研究（Tian, Xiong）との比較可能性のため0–100（＝0.0–1.0）を採用し、ラウンドナンバー問題は補足分析として報告する。

### 1.5 MlingConf 2025 (ACL Findings) — 多言語確信度推定

5言語（英語・中国語・フランス語・タイ語・**日本語**）で3つの確信度推定手法を比較。

**手法**: 確率ベース / p(True)ベース / 自己言語化（verbalized）

**主要知見**:
- **Native-Tone Prompting**: 質問の言語的背景を評価してから対応言語で回答させると、精度・確信度推定の両方が改善
- 英語での calibration は他言語より**有意に優秀**
- 言語非依存タスクでは言語間差は小さい
- 日本語は「中資源言語」に該当し、英語より calibration が劣化する傾向

**本研究への示唆**:
- 日本語プロンプトでは native-tone（日本語での自然な指示）が重要
- RQ4（日英比較）では英語が優位になることが予想される → その差の定量化が貢献

### 1.6 ADVICE 2025 (arXiv:2510.10913) — 回答依存型確信度推定

**核心的発見**: 確信度の**回答非依存性**（answer-independence）が過信の主因。

- モデルは自分の回答内容に関わらず同じ確信度を出す傾向がある
- 回答に確信度を**接地（ground）**させることで過信が軽減
- ScoreText（高/中/低）vs ScoreNumber（0–9）の形式比較

**本研究への示唆**: Verb.2S（二段階）は回答後に確信度を問うため、回答への接地が自然に発生 → calibration 改善が期待できる理論的根拠。

### 1.7 その他の重要知見

| 論文 | 知見 | 本研究への影響 |
|---|---|---|
| "Wired for Overconfidence" (2025, arXiv:2604.01457) | 過信はアーキテクチャに内在する機構的問題 | プロンプト設計の限界を認識 |
| "Verbalized Confidence Triggers Self-Verification" (2025, arXiv:2506.03723) | 確信度言語化が自己検証を誘発 | Verb.2Sの理論的裏付け |
| ConfTuner (NeurIPS 2025) | Tokenized Brier Score でfine-tuning | black-box APIでは適用不可、比較対象として言及 |
| "Influences on LLM Calibration" (2025, arXiv:2501.03991) | 応答一致・損失関数・プロンプトスタイルの影響 | プロンプトスタイルの選択根拠 |

---

## 2. 本研究のプロンプト設計方針

### 2.1 設計原則

先行研究から導出した設計原則:

1. **比較可能性**: Tian 2023・Xiong 2024 のプロンプト構造を踏襲し、結果の比較を可能にする
2. **日本語ネイティブトーン**: MlingConf 2025 の知見に基づき、自然な日本語で指示する（英語からの直訳を避ける）
3. **出力形式の厳密化**: 自動パース可能な構造化出力を要求する
4. **スケール一貫性**: 0.0–1.0（= 0–100%）スケールで統一、先行研究と比較可能
5. **ドメイン適応**: 回答形式がドメインごとに異なるため、ドメイン固有の指示を含める
6. **過信抑制の不使用**: 「自信を持ちすぎないでください」等の誘導的指示は加えない（バイアスの導入を避ける）

### 2.2 先行研究のプロンプト構成要素の分析

Xiong et al. 2024 のプロンプト構造を分解:

| 構成要素 | 内容 | 必要性 |
|---|---|---|
| **タスク記述** | 何をするかの説明 | 必須 |
| **確信度の定義** | 「確信度＝回答が正しい確率」の明示 | 必須（曖昧さ回避） |
| **出力形式指定** | 回答と確信度のフォーマット | 必須（自動パース） |
| **回答型の制約** | "ONLY the number" 等 | 必須（冗長出力防止） |
| **追加説明の禁止** | "don't give me the explanation" | Verb.1Sのみ |
| **推論の明示要求** | "analyze step by step" | CoT変種のみ |

### 2.3 ドメイン別の回答形式定義

| ドメイン | データセット | 回答形式 | パース方法 |
|---|---|---|---|
| 数学 | MGSM | 数値（整数または小数） | 正規表現で数値抽出 |
| 常識QA | JCommonsenseQA | 選択肢ラベル（0–4） | ラベル文字列一致 |
| 知識QA | JMMLU | 選択肢ラベル（A–D） | ラベル文字列一致 |
| 翻訳 | FLORES-200 | 自由形式テキスト | COMET スコア閾値 |

---

## 3. プロンプトテンプレート（確定案）

### 3.1 Verb.1S — 回答と確信度の同時出力

**理論的位置づけ**: Xiong 2024 の Vanilla 方式に対応。最も基本的な手法であり、ベースライン条件。

**設計根拠**:
- Xiong 2024 の Vanilla プロンプト構造を日本語に適応
- 確信度の定義を明示（「正しい確率」）→ 曖昧さを排除
- 出力形式を厳密に指定 → 自動パースを保証
- 説明の追加を禁止 → 確信度への推論プロセスの影響を統制

#### 数学（MGSM）
```
以下の数学の問題を読み、回答と、その回答が正しいと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]
確信度: [0.0〜1.0の数値]
```

#### 常識QA（JCommonsenseQA）
```
以下の問題を読み、最も適切な選択肢の番号と、その回答が正しいと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

問題: {question}
選択肢: {choices}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [選択肢の番号のみ]
確信度: [0.0〜1.0の数値]
```

#### 知識QA（JMMLU）
```
以下の問題を読み、最も適切な選択肢の記号と、その回答が正しいと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

問題: {question}
A. {choice_A}
B. {choice_B}
C. {choice_C}
D. {choice_D}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/Dのいずれか]
確信度: [0.0〜1.0の数値]
```

#### 翻訳（FLORES-200）
```
以下の日本語の文を英語に翻訳し、その翻訳が正確であると思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

原文: {source_text}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳文]
確信度: [0.0〜1.0の数値]
```

### 3.2 Verb.2S — 二段階の確信度引き出し

**理論的位置づけ**: Xiong 2024 の Self-Probing 方式・Tian 2023 の Two-Stage に対応。回答生成と確信度評価の認知プロセスを分離する。

**設計根拠**:
- ADVICE 2025 の知見: 回答に確信度を接地（ground）させることで過信を軽減
- Xiong 2024 の Self-Probing: 自分の回答を改めて評価する構造
- 二段階分離により、回答生成時のバイアスが確信度に直接伝播することを防止
- 「あなたの回答」を明示的に提示 → 回答依存型の確信度を誘発

#### Turn 1（全ドメイン共通の構造）

**数学（MGSM）:**
```
以下の数学の問題に回答してください。

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]
```

**常識QA（JCommonsenseQA）:**
```
以下の問題に対して、最も適切な選択肢の番号を答えてください。

問題: {question}
選択肢: {choices}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [選択肢の番号のみ]
```

**知識QA（JMMLU）:**
```
以下の問題に対して、最も適切な選択肢の記号を答えてください。

問題: {question}
A. {choice_A}
B. {choice_B}
C. {choice_C}
D. {choice_D}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/Dのいずれか]
```

**翻訳（FLORES-200）:**
```
以下の日本語の文を英語に翻訳してください。

原文: {source_text}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳文]
```

#### Turn 2（全ドメイン共通）
```
あなたは先ほどの問題に対して「{answer}」と回答しました。
この回答が正しい確率を0.0（まったく自信がない）から1.0（完全に確信している）の数値で答えてください。

以下の形式で回答してください。形式以外の出力はしないでください。
確信度: [0.0〜1.0の数値]
```

**実装上の注意**: Turn 1 と Turn 2 は同一の会話セッション（コンテキスト）内で実行する。これにより、モデルが自分の回答を「記憶」した状態で確信度を評価できる。APIの `messages` 配列に Turn 1 の応答を assistant メッセージとして含める。

### 3.3 Ling.1S — 言語表現による確信度

**理論的位置づけ**: Tian 2023 の Linguistic 方式に対応。数値の代わりに言語表現で確信度を表現させ、事後的に数値マッピングを行う。

**設計根拠**:
- 数値表現のラウンドナンバー問題（Dai 2025: 78%+が端数なし値に集中）を回避
- 言語表現はモデルの自然な出力に近く、より「素直な」メタ認知を反映する可能性
- 5段階のカテゴリ的確信度は、Likert尺度と類似し解釈が直感的
- 日本語の自然な確信度表現を使用（MlingConf の native-tone 原則）

#### 言語表現と数値マッピング

| 表現 | 数値マッピング | 英語対応 | 選定根拠 |
|---|---|---|---|
| ほぼ確実 | 0.95 | Almost certain | 高確信の上限を0.95とし完全確信を避ける |
| かなり自信がある | 0.80 | Quite confident | 高〜中高の確信を表現 |
| どちらともいえない | 0.50 | Uncertain / 50-50 | 中立点 |
| あまり自信がない | 0.25 | Not very confident | 低確信 |
| ほとんどわからない | 0.05 | Almost no idea | 最低確信（0.0を避ける） |

**マッピング値の根拠**:
- 5段階の等間隔マッピング（0.05, 0.25, 0.50, 0.80, 0.95）ではなく、確率空間で対称的な配置を採用
- 端点を0.0/1.0ではなく0.05/0.95に設定 → 完全な確信/無知は非現実的であり、ECE計算でのビン境界問題を回避
- Lin et al. 2022 (TMLR) "Teaching Models to Express Their Uncertainty in Words" のマッピング方式を参考

**感度分析**: マッピング値を ±0.05 変動させた場合のECE変化を補足分析として報告する。

#### プロンプトテンプレート

**数学（MGSM）:**
```
以下の数学の問題を読み、回答と、その回答に対する自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

- ほぼ確実
- かなり自信がある
- どちらともいえない
- あまり自信がない
- ほとんどわからない

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]
確信度: [上記5つの表現から1つ]
```

**常識QA（JCommonsenseQA）:**
```
以下の問題を読み、最も適切な選択肢の番号と、その回答に対する自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

- ほぼ確実
- かなり自信がある
- どちらともいえない
- あまり自信がない
- ほとんどわからない

問題: {question}
選択肢: {choices}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [選択肢の番号のみ]
確信度: [上記5つの表現から1つ]
```

**知識QA（JMMLU）:**
```
以下の問題を読み、最も適切な選択肢の記号と、その回答に対する自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

- ほぼ確実
- かなり自信がある
- どちらともいえない
- あまり自信がない
- ほとんどわからない

問題: {question}
A. {choice_A}
B. {choice_B}
C. {choice_C}
D. {choice_D}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/Dのいずれか]
確信度: [上記5つの表現から1つ]
```

**翻訳（FLORES-200）:**
```
以下の日本語の文を英語に翻訳し、その翻訳に対する自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

- ほぼ確実
- かなり自信がある
- どちらともいえない
- あまり自信がない
- ほとんどわからない

原文: {source_text}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳文]
確信度: [上記5つの表現から1つ]
```

---

## 4. RQ4用 英語プロンプト

RQ4（日英比較）で使用する英語版プロンプト。日本語版と**構造的に同一**であることが重要。

### 4.1 Verb.1S (English)

**Math (MGSM-en):**
```
Read the following math problem and provide your answer along with your confidence
that the answer is correct. Express your confidence as a number from 0.0 (no confidence)
to 1.0 (completely certain).

Question: {question}

Respond in exactly the following format. Do not include any other output.
Answer: [number only]
Confidence: [a number between 0.0 and 1.0]
```

**Knowledge QA (MMLU):**
```
Read the following question and provide the most appropriate answer choice along with
your confidence that the answer is correct. Express your confidence as a number from
0.0 (no confidence) to 1.0 (completely certain).

Question: {question}
A. {choice_A}
B. {choice_B}
C. {choice_C}
D. {choice_D}

Respond in exactly the following format. Do not include any other output.
Answer: [one of A/B/C/D]
Confidence: [a number between 0.0 and 1.0]
```

**Translation (FLORES-200 en→ja):**
```
Translate the following English sentence into Japanese, and provide your confidence
that the translation is accurate. Express your confidence as a number from 0.0
(no confidence) to 1.0 (completely certain).

Source: {source_text}

Respond in exactly the following format. Do not include any other output.
Translation: [Japanese translation]
Confidence: [a number between 0.0 and 1.0]
```

### 4.2 Verb.2S / Ling.1S (English)

英語版の Verb.2S・Ling.1S も同様の構造的対応で作成する（ここでは Verb.1S を代表例として提示）。

Ling.1S 英語版の表現マッピング:

| 英語表現 | 数値 | 日本語対応 |
|---|---|---|
| Almost certain | 0.95 | ほぼ確実 |
| Quite confident | 0.80 | かなり自信がある |
| Uncertain | 0.50 | どちらともいえない |
| Not very confident | 0.25 | あまり自信がない |
| Almost no idea | 0.05 | ほとんどわからない |

---

## 5. 設計上の重要な注意点

### 5.1 CoT（Chain-of-Thought）を独立条件にしない理由

Xiong 2024 では CoT 変種を評価しているが、本研究では独立条件として採用しない:

1. **過信助長リスク**: CoTは推論の一貫性を高めるが、それが**より高い確信度報告**につながり、calibration を悪化させる場合がある (Xiong 2024; "Wired for Overconfidence" 2025)
2. **交絡因子**: CoTは回答の正答率自体を変化させるため、確信度プロンプト設計の効果と分離が困難
3. **実験条件の制御**: 3条件（Verb.1S/2S/Ling.1S）に CoT の有無を掛け合わせると 6条件に倍増し、コスト・複雑性が過大
4. **先行研究との整合**: Tian 2023 の3方式（Numeric/Two-Stage/Linguistic）と直接比較可能

ただし、**将来の拡張可能性**として §7「今後の課題」で言及する。

### 5.2 0.0–1.0 スケール vs 0–100% スケール vs 0–20 スケール

| スケール | 利点 | 欠点 | 先行研究での使用 |
|---|---|---|---|
| 0–100% | 直感的、先行研究で最多 | ラウンドナンバー集中（Dai 2025） | Xiong 2024, Yang 2024 |
| 0.0–1.0 | 確率として自然、計算に直結 | やや直感的でない | Tian 2023 |
| 0–20 | meta-d' 最良（Dai 2025） | 先行研究と比較不能 | Dai 2025 のみ |

**本研究の選択: 0.0–1.0**
- 確率値として直接ECE計算に使用できる
- Tian 2023 と同一スケール
- 0–100%と実質同等だが、「確率」であることが明示的
- ラウンドナンバー問題の分析は 0.1 刻みの分布として報告

### 5.3 temperature 設定

- **temperature = 0**（決定的出力）を使用
- 理由: 同一問題に対する確信度のばらつきを排除し、プロンプト方式間の比較を純粋にする
- Xiong 2024 では sampling-based 手法（temperature > 0 で複数サンプル）も評価しているが、本研究はプロンプト設計の効果に焦点を置くため決定的設定を採用

### 5.4 システムプロンプトの統制

全条件で以下の統制を行う:
- **システムプロンプトは使用しない**（または最小限の共通プロンプト）
- モデルのデフォルト動作への影響を排除
- システムプロンプトの有無自体が交絡因子になることを防止

### 5.5 パイロット実験での検証項目

本格実験の前に、各ドメイン10問程度でパイロット実験を実施し、以下を確認:

1. **出力形式の遵守率**: 指定形式通りに出力されるか（パース成功率 > 95% を要求）
2. **確信度の分布**: 特定の値に極端に集中していないか
3. **Ling.1S の表現遵守**: 5つの表現以外の出力がないか
4. **Verb.2S の実装**: Turn 2 で Turn 1 の回答が適切に参照されているか
5. **翻訳ドメイン**: 確信度が他ドメインと著しく異なるパターンがないか

パース失敗時のフォールバック:
- 正規表現での緩い抽出を試みる（例: "確信度は0.8です" → 0.8 を抽出）
- それでも失敗した場合は NA として記録し、分析から除外（除外率を報告）

---

## 6. 先行研究との比較表

| 要素 | Tian 2023 | Xiong 2024 | 本研究 |
|---|---|---|---|
| **言語** | 英語 | 英語 | **日本語**（+ 英語比較） |
| **スケール** | 0.0–1.0 | 0–100% | 0.0–1.0 |
| **条件数** | 3 | 5 | 3 |
| **Verb.1S 相当** | ✓ (Top-K) | ✓ (Vanilla) | ✓ |
| **Verb.2S 相当** | ✓ (Two-Stage) | ✓ (Self-Probing) | ✓ |
| **Ling.1S 相当** | ✓ (Linguistic) | ✗ | ✓ |
| **CoT** | ✗ | ✓ | ✗（理由: §5.1） |
| **Top-K** | ✓ | ✓ | ✗（実装コスト高） |
| **ドメイン数** | 3 | 5 | 4 |
| **モデル数** | 3 | 5 | 4–5 |
| **temperature** | 記載なし | 0 & 0.5 | 0 |

---

## 7. 補足分析計画

本格実験データ取得後に実施する補足分析:

1. **ラウンドナンバー分析**: Verb.1S/2S の確信度分布における 0.1 刻み集中度
2. **Ling.1S マッピング感度分析**: マッピング値 ±0.05 での ECE 変動
3. **ドメイン × プロンプト方式の交互作用**: ドメインによって最適なプロンプト方式が異なるか
4. **パース失敗率の報告**: 条件別の出力形式遵守率

---

## 8. 参考文献

1. Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. *EMNLP 2023*.
2. Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. *ICLR 2024*. [Code: github.com/MiaoXiong2320/llm-uncertainty]
3. Yang, D., Tsai, Y.-H. H., & Yamada, M. (2024). On Verbalized Confidence Scores for LLMs. *arXiv:2412.14737*.
4. Dai, Y. (2025). Rescaling Confidence: What Scale Design Reveals About LLM Metacognition. *arXiv:2603.09309*.
5. Xue, B., et al. (2025). MlingConf: A Comprehensive Study of Multilingual Confidence Estimation on Large Language Models. *Findings of ACL 2025*.
6. Seo, K. J., et al. (2025). ADVICE: Answer-Dependent Verbalized Confidence Estimation. *arXiv:2510.10913*.
7. Liu, S., et al. (2025). ConfTuner: Training Large Language Models to Express Their Confidence Verbally. *NeurIPS 2025*.
8. Lin, S., Hilton, J., & Evans, O. (2022). Teaching Models to Express Their Uncertainty in Words. *TMLR*.
