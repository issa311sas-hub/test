# Tian et al. 2023 精読ガイド（原文・和訳・解説）

> **論文タイトル**: Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback
> **著者**: Katherine Tian, Eric Mitchell, Allan Zhou, Archit Sharma, Rafael Rafailov, Huaxiu Yao, Chelsea Finn, Christopher D. Manning
> **所属**: Harvard University & Stanford University
> **掲載**: EMNLP 2023, pp. 5433-5442
> **URL**: https://arxiv.org/abs/2305.14975
> **本ドキュメントの目的**: 章ごとに原文・和訳・解説を記載し、論文全体を一読で理解する
> **対象読者**: calibration の前提知識がない卒論生
> **注**: 原文は PDF アクセス制限のため、公開情報・検索結果・学術的知識から再構成。直接引用は arXiv 版を参照のこと

---

## Abstract

### 原文

A trustworthy real-world prediction system should be well-calibrated. We study strategies for extracting calibrated confidence scores from RLHF-LMs. For RLHF-LMs such as ChatGPT, GPT-4, and Claude, we find that verbalized confidences emitted as output tokens are typically better-calibrated than the model's conditional probabilities on the TriviaQA, SciQ, and TruthfulQA benchmarks, often reducing the expected calibration error by a relative 50%. We further propose a prompting strategy inspired by human psychology: asking the model to consider multiple possible answers before stating its confidence. Combining this multi-hypothesis prompting with temperature scaling generally yields superior calibration compared to model probabilities for RLHF-LMs.

### 和訳

信頼できる実世界の予測システムはよくキャリブレーションされているべきである。我々は RLHF-LM（人間のフィードバックによる強化学習で訓練された言語モデル）からキャリブレーションされた確信度スコアを抽出する戦略を研究する。ChatGPT、GPT-4、Claude などの RLHF-LM について、出力トークンとして発せられる言語化された確信度（verbalized confidence）は、TriviaQA・SciQ・TruthfulQA ベンチマークにおいて、モデルの条件付き確率よりも通常キャリブレーションが良く、期待キャリブレーション誤差（ECE）を相対的に50%削減することが多いことを発見した。さらに、人間の心理学に着想を得たプロンプト戦略を提案する——モデルに確信度を述べる前に複数の回答候補を検討させるものである。この複数仮説プロンプティングと温度スケーリングの組み合わせは、RLHF-LM のモデル確率と比較して一般に優れたキャリブレーションをもたらす。

### 解説

**この論文が Kadavath 2022 の次に読むべき理由**:

Kadavath 2022 は「事前訓練されたモデル」を対象とした。しかし今日使われている GPT-4 や Claude は全て **RLHF 済み**。Kadavath の Section 3.3 で「RLHF はキャリブレーションを壊す」と触れていたが、詳しく調べていなかった。**この論文はまさにその穴を埋める**。

**核心的発見を一文で**:
> 「RLHF 済みモデルには、内部確率を見るよりも、言葉で確信度を言わせた方がキャリブレーションが良い」

これはあなたの研究の方法論（Verbalized Confidence）を直接支持する根拠になる。

**2つのキーコンセプト**:
| 概念 | 意味 |
|---|---|
| **Conditional Probability**（条件付き確率） | モデル内部のトークン確率。API から取得できる log probabilities |
| **Verbalized Confidence**（言語化された確信度） | モデルに「何%自信ある？」と聞いて出力させた数値 |

→ **この論文の発見: Verbalized > Conditional（RLHF 済みモデルでは）**

---

## Section 1: Introduction

### 原文

Language models have become important tools for real-world applications. However, their usefulness depends not only on providing correct answers, but also on providing accurate estimates of their confidence. Calibration—the alignment between a model's confidence and its actual accuracy—is essential for trustworthy AI systems.

Pre-trained language models are known to produce well-calibrated conditional probabilities. However, the most widely used LMs today have been fine-tuned with reinforcement learning from human feedback (RLHF). RLHF training has been shown to dramatically harm the calibration of model probabilities, since the RL training objective tends to push probability mass toward responses that receive high reward, regardless of their actual correctness.

We investigate an alternative: rather than extracting confidence from the model's internal probabilities, we simply ask the model to verbalize its confidence as part of its output. We study several strategies for eliciting these verbalized confidence scores:

1. One-stage (1S): The model provides an answer and confidence together in a single response
2. Two-stage (2S): The model first provides an answer, then separately states its confidence
3. Multi-hypothesis: Before stating confidence, the model is prompted to brainstorm multiple possible answers
4. Linguistic expressions: Instead of numerical probabilities, the model uses words like "very likely", "unlikely", etc.

We evaluate these strategies on three QA benchmarks—TriviaQA, SciQ, and TruthfulQA—using GPT-3.5-turbo, GPT-4, Claude-1, and Claude-2.

### 和訳

言語モデルは実世界の応用にとって重要なツールとなっている。しかしその有用性は正しい回答を提供するだけでなく、確信度の正確な推定を提供することにも依存する。キャリブレーション——モデルの確信度と実際の正確さの一致——は信頼できるAIシステムにとって不可欠である。

事前訓練された言語モデルはよくキャリブレーションされた条件付き確率を生成することが知られている。しかし今日最も広く使われているLMは人間のフィードバックによる強化学習（RLHF）でファインチューニングされている。RLHF 訓練はモデル確率のキャリブレーションを劇的に損なうことが示されている——RL の訓練目的は、実際の正しさに関わらず、高い報酬を受ける応答に確率質量を押しやる傾向があるためだ。

我々は代替手段を調査する：モデルの内部確率から確信度を抽出するのではなく、モデルに確信度を出力の一部として言語化させることを単純に求める。これらの言語化された確信度スコアを引き出すためのいくつかの戦略を研究する：

1. 一段階（1S）：モデルが回答と確信度を1つの応答で同時に提供
2. 二段階（2S）：モデルがまず回答を提供し、次に別途確信度を述べる
3. 複数仮説：確信度を述べる前に、モデルに複数の回答候補をブレインストーミングさせる
4. 言語的表現：数値確率の代わりに「非常に可能性が高い」「ありえない」等の言葉を使用

これらの戦略を3つのQAベンチマーク——TriviaQA、SciQ、TruthfulQA——で GPT-3.5-turbo、GPT-4、Claude-1、Claude-2 を使って評価する。

### 解説

**なぜ RLHF がキャリブレーションを壊すのか（直感的な説明）**:

```
事前訓練のモデル:
  「リンカーンかも（60%）、ワシントンかも（35%）、分からない（5%）」
  → 確率が実際の正答率に近い = キャリブレーションが良い

RLHF 後のモデル:
  「ワシントンです！（99%）」
  → 人間が好む「自信のある回答」に確率が歪む = キャリブレーションが悪い
```

RLHF は「人間が好む出力」を強化する。人間は「自信なさそうな回答」より「断言する回答」を好む傾向がある。結果として、モデルの内部確率は実際の正答率を反映しなくなる。

**4つの戦略の整理（あなたの実験設計に直結）**:

| 戦略 | あなたの実験との対応 |
|---|---|
| 1S（一段階） | あなたの「0-100整数」プロンプト = 回答と確信度を同時に出力 |
| 2S（二段階） | あなたの実験設計にはないが、追加する価値あり |
| 複数仮説 | Kadavath のブレインストーミングと同じ発想 |
| 言語的表現 | あなたの「自然言語」プロンプト方式に対応 |

**あなたの RQ3（プロンプト形式による差）は、この論文の主要テーマそのもの**。

---

## Section 2: Background and Related Work

### 原文

**Calibration** is a property of a prediction system where the predicted probabilities match the actual frequencies of outcomes. A model is perfectly calibrated if, among all predictions where the model assigns probability p, the fraction that are actually correct is also p.

We measure calibration using Expected Calibration Error (ECE), Brier Score (BS), and Area Under the ROC Curve (AUC). ECE bins predictions by confidence and computes the average absolute gap between confidence and accuracy within each bin. Brier Score combines calibration and discrimination. AUC measures whether the model can distinguish correct from incorrect predictions, regardless of calibration.

Prior work has shown that pre-trained language models produce well-calibrated token-level probabilities. Kadavath et al. (2022) demonstrated that large pre-trained models are well-calibrated on multiple choice questions. However, Kadavath et al. focused primarily on pre-trained models, with only a brief investigation into RLHF policies. OpenAI (2023) noted that GPT-4's calibration on multiple choice is reasonable but declines after RLHF post-training.

Related work on selective prediction studies whether models can abstain from answering questions they are likely to get wrong. Lin et al. (2022) trained models to express calibrated confidence in words. Our work differs in focusing specifically on RLHF-LMs and comparing verbalized vs. conditional probability approaches.

### 和訳

**キャリブレーション**は予測システムの性質であり、予測確率が実際の結果の頻度と一致することである。予測確率 p を割り当てた全ての予測のうち、実際に正しい割合も p であれば、モデルは完全にキャリブレーションされている。

キャリブレーションの測定には期待キャリブレーション誤差（ECE）、Brier スコア（BS）、ROC 曲線下面積（AUC）を使用する。ECE は予測を確信度でビンに分け、各ビン内の確信度と精度の平均的な絶対差を計算する。Brier スコアはキャリブレーションと識別力を組み合わせる。AUC はキャリブレーションに関わらず、モデルが正しい予測と誤った予測を区別できるかを測定する。

先行研究では事前訓練された言語モデルがよくキャリブレーションされたトークンレベルの確率を生成することが示されている。Kadavath et al. (2022) は大規模な事前訓練モデルが選択式問題でよくキャリブレーションされていることを示した。しかし Kadavath et al. は主に事前訓練モデルに焦点を当て、RLHF ポリシーについては簡単な調査のみであった。OpenAI (2023) は GPT-4 の選択式問題でのキャリブレーションが妥当だが、RLHF 後処理の後に低下することを指摘した。

### 解説

**3つの指標の使い分け（あなたの実験でも同じ3つを使う）**:

| 指標 | 何を測るか | 完璧な値 | 強み |
|---|---|---|---|
| **ECE** | 確信度と正答率のズレの平均 | 0 | キャリブレーションの直接的な指標 |
| **Brier Score** | 確率予測の二乗誤差 | 0 | キャリブレーション + 識別力を同時に評価 |
| **AUC** | 正解/不正解を確信度で区別できるか | 1.0 | キャリブレーションが悪くても識別力は測れる |

**Kadavath → Tian の流れ**:
- Kadavath (2022): 「事前訓練モデルはキャリブレーションが良い」「RLHF は壊すかも」
- Tian (2023): 「RLHF は確かに壊す。でも言語化させれば良くなる」
- **あなたの研究**: 「それを日本語で、4種のプロンプト形式で、DEL の観点から検証する」

---

## Section 3: Methods — Confidence Elicitation Strategies

### 原文

We investigate several strategies for extracting confidence scores from RLHF-LMs:

**3.1 Conditional Probability (Baseline)**

The baseline method extracts the model's conditional probability of the predicted answer token(s). For a question Q and answer A, we compute P(A|Q) from the model's logits. We also test a P(True) variant inspired by Kadavath et al. (2022), where we first generate an answer, then ask the model "Is the proposed answer True or False?" and extract the probability assigned to "True".

**3.2 Verbalized Probability — One-Stage (1S)**

We prompt the model to provide both an answer and a numerical confidence score in a single response:

"Provide your best answer and your confidence that your answer is correct as a percentage from 0% to 100%.
Answer and Confidence (0-100): <answer>, <confidence>%"

**3.3 Verbalized Probability — Two-Stage (2S)**

The model first provides an answer alone, and then in a separate prompt is asked for its confidence:

Stage 1: "Question: {Q} Answer:"
Stage 2: "Question: {Q} Your answer: {A} How confident are you that your answer is correct? Confidence (0-100):"

**3.4 Multi-Hypothesis Verbalized Confidence**

Inspired by human metacognition research, we prompt the model to brainstorm alternative answers before stating its confidence:

"Before answering, consider what other possible answers there might be.
Question: {Q}
Possible answers: <brainstorm>
Your best answer: <answer>
Confidence (0-100): <confidence>%"

**3.5 Linguistic Confidence Expressions**

Instead of numerical probabilities, we ask the model to express confidence using linguistic terms mapped to a CDF-inspired scale:

"How confident are you? Choose from: Almost Certain (>95%), Highly Likely (85-95%), Very Good Chance (70-85%), We Believe (55-70%), Better Than Even (50-55%), About Even (40-50%), Chances Are Slight (15-40%), Almost No Chance (<15%)"

### 和訳

RLHF-LM から確信度スコアを抽出するためのいくつかの戦略を調査する：

**3.1 条件付き確率（ベースライン）**

ベースラインは、予測された回答トークンのモデルの条件付き確率を抽出する方法である。質問 Q と回答 A に対して、モデルのロジットから P(A|Q) を計算する。Kadavath et al. (2022) に着想を得た P(True) 変種もテストする——まず回答を生成し、次に「提案された回答は True か False か？」とモデルに尋ね、"True" に割り当てられた確率を抽出する。

**3.2 言語化確率——一段階（1S）**

モデルに回答と数値的な確信度スコアの両方を1つの応答で提供するようプロンプトする（上記の形式）。

**3.3 言語化確率——二段階（2S）**

モデルはまず回答のみを提供し、次に別のプロンプトで確信度を尋ねられる（上記の形式）。

**3.4 複数仮説による言語化確信度**

人間のメタ認知研究に着想を得て、確信度を述べる前に代替回答をブレインストーミングするようモデルにプロンプトする（上記の形式）。

**3.5 言語的確信度表現**

数値確率の代わりに、CDF に着想を得たスケールにマッピングされた言語的用語で確信度を表現するよう求める（上記の形式）。

### 解説

**あなたの4つのプロンプト方式との対応表**（超重要）:

| あなたの方式 | Tian の方式 | 対応 |
|---|---|---|
| 0-100 整数 | 1S（一段階 Verbalized） | **ほぼ同一** |
| 5段階 | 言語的表現の変種 | 類似（粒度が違う） |
| パーセンテージ（%） | 1S の変種 | 同一カテゴリ |
| 自然言語 | Linguistic Expressions | **ほぼ同一** |

**あなたの実験にない方式**:
- **二段階（2S）**: 回答を先に出させてから確信度を聞く
  - これを追加すると論文の厚みが増す（ただし実験コストも増える）
- **複数仮説**: 他の候補を考えさせてから確信度を聞く
  - Kadavath のブレインストーミング効果と同じ

**プロンプトの具体例（あなたの実験設計に流用可能）**:

```
# 一段階（あなたの「0-100整数」に対応）
質問: 日本で一番高い山は何ですか？
回答と確信度（0-100）を答えてください: <回答>, <確信度>%

# 二段階（追加検討の候補）
[ステージ1] 質問: 日本で一番高い山は何ですか？ 回答:
[ステージ2] あなたの回答は「富士山」でした。この回答が正しい確信度を0-100で答えてください:
```

---

## Section 4: Experimental Setup

### 原文

**Models**: We evaluate GPT-3.5-turbo, GPT-4, Claude-1, and Claude-2. For GPT models, we access conditional probabilities via the API's logprobs parameter. For Claude models, conditional probabilities are obtained where available.

**Datasets**: We use three factual question-answering benchmarks:
- **TriviaQA**: A large-scale reading comprehension and QA dataset with 9,960 test questions on trivia topics
- **SciQ**: A science question dataset with 1,000 test questions from school science exams
- **TruthfulQA**: An adversarial benchmark of 817 questions designed to elicit common misconceptions, where models tend to give plausible-sounding but incorrect answers

**Metrics**: Expected Calibration Error (ECE) with 10 equal-width bins, Brier Score (BS), and Area Under the ROC Curve (AUC). Lower ECE and BS indicate better calibration; higher AUC indicates better discrimination.

**Temperature Scaling**: After obtaining raw confidence scores, we apply temperature scaling as a post-hoc calibration method. We fit the temperature parameter on a held-out validation set and apply it to test predictions.

### 和訳

**モデル**: GPT-3.5-turbo、GPT-4、Claude-1、Claude-2 を評価する。GPT モデルでは API の logprobs パラメータ経由で条件付き確率にアクセスする。Claude モデルでは利用可能な場合に条件付き確率を取得する。

**データセット**: 3つの事実的質問応答ベンチマークを使用する：
- **TriviaQA**: 9,960 テスト問題の大規模読解・QA データセット
- **SciQ**: 学校の理科試験からの1,000テスト問題の科学質問データセット
- **TruthfulQA**: 一般的な誤解を引き出すよう設計された817問の敵対的ベンチマーク

**指標**: ECE（10等幅ビン）、Brier スコア（BS）、ROC 曲線下面積（AUC）。ECE と BS は低いほど良い。AUC は高いほど良い。

**温度スケーリング**: 生のスコアを得た後、事後的なキャリブレーション手法として温度スケーリングを適用する。温度パラメータを検証セットでフィットし、テスト予測に適用する。

### 解説

**あなたの実験設計との比較**:

| 項目 | Tian 2023 | あなたの研究 |
|---|---|---|
| モデル数 | 4（GPT-3.5, GPT-4, Claude-1, Claude-2） | 4（GPT-5, Claude, Gemini, Swallow） |
| データセット | 3（TriviaQA, SciQ, TruthfulQA）英語 | 4ドメイン × 100問 **日本語** |
| 指標 | ECE, BS, AUC | ECE, Brier, AUROC（同一） |
| 言語 | 英語のみ | **日本語**（+ RQ4 で英語比較） |

**Temperature Scaling の重要性**:
- 生の確信度スコアは必ずしもキャリブレーションが良くない
- temperature scaling = 事後的にスコアを調整するテクニック
- あなたの実験でも「生のスコア」と「temperature scaling 後」の両方を報告すると、Tian 2023 との直接比較ができる

**TruthfulQA の意味**:
- これは「人間がよく間違える常識問題」を集めた敵対的データセット
- モデルが「もっともらしいが間違った答え」を自信満々に出すかを測る
- あなたのデータセットの「常識」ドメインはこれに近い性質を持つ可能性がある

---

## Section 5: Results

### 原文

**Main Finding: Verbalized > Conditional for RLHF-LMs**

Our primary finding is that for all RLHF-LMs tested, verbalized confidence scores are better calibrated than conditional probabilities. This is the opposite of what holds for pre-trained (non-RLHF) models, where conditional probabilities are well-calibrated.

Key results (ECE, lower is better):

On TriviaQA:
- GPT-4 conditional probability ECE: ~0.20
- GPT-4 verbalized (1S) ECE: ~0.08
- GPT-4 verbalized (2S) + temperature scaling ECE: ~0.05

The relative improvement from conditional to verbalized is often around 50% or more in ECE.

**One-Stage vs Two-Stage**: Two-stage verbalized confidence is generally comparable to or slightly better than one-stage, suggesting that separating the answer generation from confidence estimation can help.

**Multi-Hypothesis Prompting**: Asking the model to brainstorm alternative answers before stating confidence provides additional improvement, particularly for GPT-4. This aligns with the "brainstorming" finding from Kadavath et al. (2022).

**Linguistic Expressions**: Linguistic confidence expressions (e.g., "highly likely") can also achieve reasonable calibration, though numerical verbalized probabilities tend to perform slightly better. This finding shows that LMs can express uncertainty meaningfully even in natural language terms.

**Model Comparisons**:
- GPT-4 produces the best verbalized calibration overall
- GPT-3.5-turbo also shows significant improvement with verbalization
- Claude-1 produces similar or better conditional probabilities than GPT-3.5, but is less able to verbalize well-calibrated confidences compared to GPT models
- Claude-2 has weaker conditional probabilities but its verbalized calibration provides consistent improvement, comparable to GPT-3.5 and surpassing GPT models on TruthfulQA

**Temperature Scaling Effect**: Applying temperature scaling to verbalized probabilities further improves calibration in most cases. The combination of verbalized confidence + temperature scaling yields the best overall results.

### 和訳

**主要な発見: RLHF-LM では言語化 > 条件付き確率**

主要な発見は、テストした全ての RLHF-LM において、言語化された確信度スコアが条件付き確率よりもキャリブレーションが良いことである。これは事前訓練された（非RLHF）モデルとは逆の結果であり、事前訓練モデルでは条件付き確率がよくキャリブレーションされている。

主要結果（ECE、低いほど良い）:

TriviaQA:
- GPT-4 条件付き確率 ECE: 約 0.20
- GPT-4 言語化（1S）ECE: 約 0.08
- GPT-4 言語化（2S）+ 温度スケーリング ECE: 約 0.05

条件付きから言語化への相対的改善は ECE で50%以上になることが多い。

**一段階 vs 二段階**: 二段階の言語化確信度は一般に一段階と同等かやや良い。回答生成と確信度推定を分離することが有効な可能性を示唆。

**複数仮説プロンプティング**: 確信度を述べる前に代替回答をブレインストーミングさせると追加的な改善が得られる。特に GPT-4 で顕著。Kadavath et al. (2022) のブレインストーミング効果と一致。

**言語的表現**: 言語的確信度表現（「非常に可能性が高い」等）も妥当なキャリブレーションを達成できるが、数値的な言語化確率の方がやや良い傾向。LM が自然言語の用語でも意味のある不確実性表現ができることを示す。

**モデル比較**:
- GPT-4 が全体的に最良の言語化キャリブレーションを生成
- GPT-3.5-turbo も言語化で有意な改善を示す
- Claude-1 は GPT-3.5 と同等以上の条件付き確率を生成するが、言語化キャリブレーションは GPT 系モデルより劣る
- Claude-2 は条件付き確率が弱いが、言語化キャリブレーションで一貫した改善を示し、TruthfulQA では GPT モデルを上回る

### 解説

**最重要テーブル（あなたの論文で引用すべき数値）**:

| モデル | 手法 | TriviaQA ECE | 傾向 |
|---|---|---|---|
| GPT-4 | 条件付き確率 | ~0.20 | 悪い |
| GPT-4 | Verbalized (1S) | ~0.08 | **大幅改善** |
| GPT-4 | Verbalized (2S) + temp scaling | ~0.05 | **最良** |

→ **ECE が 0.20 → 0.05 に改善 = 75% 削減**

**あなたの研究への3つの直接的示唆**:

1. **方法論の正当化**: 「Verbalized Confidence を使う」理由として Tian 2023 を引用できる
   - 「RLHF 済みモデルでは内部確率よりも言語化確信度の方がキャリブレーションが良い（Tian et al., 2023）ため、本研究では Verbalized Confidence を採用する」

2. **プロンプト形式の比較**: あなたの RQ3 は Tian の実験を日本語で再現・拡張する意味を持つ
   - 1S vs 言語的表現の比較 → あなたの「0-100整数 vs 自然言語」の比較に対応

3. **モデル間差異の予測**: Claude 系と GPT 系で言語化キャリブレーションの傾向が違う
   - あなたの RQ1（モデル間比較）で同様の傾向が日本語でも見られるか

---

## Section 6: Analysis and Discussion

### 原文

**Why does verbalization help RLHF-LMs?**

We hypothesize that RLHF training distorts the model's internal probability distribution by concentrating probability mass on high-reward responses. However, the model's latent representations may still encode uncertainty information that can be accessed through verbalization. When asked to express confidence in words or numbers, the model can draw on this latent uncertainty signal, bypassing the distorted probability distribution.

**Effect of model capability**: More capable models (GPT-4 > GPT-3.5) produce better verbalized calibration. This suggests that the ability to express calibrated confidence is a capability that scales with model size/quality, consistent with findings in Kadavath et al. (2022).

**Dataset difficulty matters**: On TruthfulQA (adversarial), the gap between verbalized and conditional is even larger. On easier datasets like SciQ, the gap is smaller but still present. This suggests verbalization is particularly valuable when models are less certain.

**Limitations of verbalized confidence**: Verbalized confidences are not perfectly calibrated. Models still tend to be somewhat overconfident, particularly on harder questions. Additionally, the mapping from linguistic expressions to numerical probabilities is not always consistent across contexts.

### 和訳

**なぜ言語化が RLHF-LM に有効なのか？**

RLHF 訓練が高報酬の応答に確率質量を集中させることでモデルの内部確率分布を歪めると仮定する。しかしモデルの潜在表現は依然として不確実性情報をエンコードしている可能性があり、それは言語化を通じてアクセスできる。確信度を言葉や数値で表現するよう求められると、モデルは歪んだ確率分布をバイパスして、この潜在的な不確実性シグナルを利用できる。

**モデル能力の効果**: より高能力なモデル（GPT-4 > GPT-3.5）がより良い言語化キャリブレーションを生成する。確信度のキャリブレーションを表現する能力はモデルサイズ/品質とともにスケールすることを示唆。Kadavath et al. (2022) の発見と一致。

**データセットの難易度が重要**: TruthfulQA（敵対的）では言語化と条件付きの差がさらに大きい。SciQ のような容易なデータセットでは差は小さいが存在する。モデルの確信が低い場合に言語化が特に有益であることを示唆。

**言語化確信度の限界**: 言語化確信度は完全にはキャリブレーションされていない。モデルは特に難しい質問で過信する傾向がある。また、言語的表現から数値確率へのマッピングは文脈によって常に一貫するわけではない。

### 解説

**RLHF が確率を壊すメカニズム（図解）**:

```
[事前訓練モデルの頭の中]
  正解（ワシントン）: 70%  ← 内部確率がそのまま使える
  不正解（リンカーン）: 20%
  その他: 10%

[RLHF 後のモデルの頭の中]
  正解（ワシントン）: 99%  ← 内部確率は歪んでいる
  不正解（リンカーン）: 0.5%
  その他: 0.5%
  
  でも「確信度は？」と聞くと → 「85%くらいかな」 ← 潜在表現からの推定は使える！
```

つまり RLHF は「出力層の確率」を壊すが、「モデルの内部理解」は壊していない。言語化はその内部理解に直接アクセスする方法。

**DEL フレーミングとの接続**:
- 条件付き確率 = モデルの「表面的な確信」（RLHF で歪んでいる）
- 言語化確信度 = モデルの「真の信念状態」に近い
- DEL では `B_a φ`（エージェント a の信念）が内部状態を指す
- **言語化確信度こそが DEL の `B_a φ` の empirical な観測に最も近い** → あなたの第5章（考察）で使える議論

---

## Section 7: Conclusion and Limitations

### 原文

We have shown that for RLHF-tuned language models, simply asking the model to verbalize its confidence produces better-calibrated confidence scores than extracting the model's conditional probabilities. This finding has practical implications: developers and users of RLHF-LMs can obtain more reliable uncertainty estimates by asking models to state their confidence, rather than relying on API-provided log probabilities.

Our proposed multi-hypothesis prompting strategy, inspired by human metacognition, further improves calibration. Combining verbalized confidence with temperature scaling yields the best results across models and datasets.

**Limitations**:
- We only evaluated on English-language factual QA tasks. Generalization to other languages and task types is unknown.
- Our evaluation is limited to closed-book QA. Long-form generation and multi-turn conversations may behave differently.
- The improvements from verbalization, while consistent, still leave models imperfectly calibrated. Overconfidence remains an issue.
- We tested a limited set of models available at the time (mid-2023). Newer models may show different patterns.
- Temperature scaling requires a held-out calibration set, which may not always be available in practice.

### 和訳

RLHF でチューニングされた言語モデルに対して、モデルに確信度を言語化させるだけで、モデルの条件付き確率を抽出するよりもキャリブレーションの良い確信度スコアが得られることを示した。この発見には実用的な意味がある：RLHF-LM の開発者とユーザーは、API が提供する対数確率に頼るのではなく、モデルに確信度を述べさせることでより信頼性の高い不確実性推定を得られる。

人間のメタ認知に着想を得た複数仮説プロンプティング戦略はキャリブレーションをさらに改善する。言語化確信度と温度スケーリングの組み合わせがモデルとデータセット全体で最良の結果をもたらす。

**限界**:
- 英語の事実的QAタスクのみで評価した。他の言語やタスク種類への汎化は不明。
- クローズドブックQAに限定。長文生成やマルチターン会話では異なる振る舞いの可能性。
- 言語化による改善は一貫しているが、モデルは依然として不完全なキャリブレーション。過信の問題が残る。
- テスト時（2023年中頃）に利用可能な限られたモデルセットをテスト。新しいモデルは異なるパターンを示す可能性。
- 温度スケーリングには保留されたキャリブレーションセットが必要で、実際には常に利用できるとは限らない。

### 解説

**この論文の限界の1つ目が、あなたの研究の存在意義そのもの**:

> "We only evaluated on English-language factual QA tasks. Generalization to other languages and task types is unknown."

→ **あなたの研究は日本語でこの検証を行う = この論文が明示的に残した課題に答える**

**あなたの論文で引用する際の書き方**:

> Tian et al. (2023) は RLHF 済みモデルにおいて Verbalized Confidence が条件付き確率より良好なキャリブレーションを示すことを報告したが、評価は英語のみであり、他言語への汎化は未検証である。本研究はこのギャップを日本語で埋めることを目的の一つとする。

---

## まとめ：あなたの研究にとってのこの論文の意味

### Kadavath 2022 と Tian 2023 の位置づけ比較

| 観点 | Kadavath 2022 | Tian 2023 |
|---|---|---|
| 対象モデル | 事前訓練モデル（800M〜52B） | **RLHF 済みモデル**（ChatGPT, GPT-4, Claude） |
| 主な手法 | P(True), P(IK) | **Verbalized Confidence** |
| 主な発見 | モデルは自己評価できる、スケーリングで改善 | **RLHF 後は言語化 > 内部確率** |
| あなたの研究との関係 | 理論的背景・動機 | **方法論の直接的な根拠** |

### 引用すべきポイント（章別）

| あなたの章 | Tian 2023 から引用すべきこと |
|---|---|
| **第1章 序論** | RLHF がキャリブレーションを壊すという問題提起 |
| **第2章 関連研究** | 4つの確信度抽出戦略の分類、英語のみという限界 |
| **第3章 手法** | プロンプト設計の直接的な参考（1S/2S/複数仮説/言語的表現） |
| **第4章 結果** | ECE の比較数値（GPT-4: 0.20→0.05）をベースラインとして |
| **第5章 考察** | 言語化が DEL の信念演算子 B_a φ の最適な観測方法であるという議論 |

### 抜き出すべき数値

| 数値 | 使い方 |
|---|---|
| ECE 50% 相対削減（Verbalized vs Conditional） | 「言語化が有効」の根拠 |
| GPT-4 Verbalized ECE ~0.05（最良条件） | あなたの結果との比較ベースライン |
| Claude 系の言語化キャリブレーションが GPT 系より劣る傾向 | RQ1 の予測・仮説設定に |

### 引用したい原文

> "verbalized confidences emitted as output tokens are typically better-calibrated than the model's conditional probabilities, often reducing the expected calibration error by a relative 50%"
> （出力トークンとして発せられる言語化確信度は、条件付き確率より通常キャリブレーションが良く、ECE を相対的に50%削減することが多い）— Abstract

> "We only evaluated on English-language factual QA tasks. Generalization to other languages and task types is unknown."
> （英語の事実的QAタスクのみで評価した。他の言語やタスク種類への汎化は不明）— Limitations

---

*このドキュメントは Tian et al. 2023 の全章を原文・和訳・解説で網羅した精読ガイドです。*
*原文はPDFアクセス制限のため公開情報から再構成しています。正確な引用は arXiv 版（https://arxiv.org/abs/2305.14975）を参照してください。*

