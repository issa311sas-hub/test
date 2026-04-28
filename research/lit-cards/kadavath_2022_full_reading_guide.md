# Kadavath et al. 2022 精読ガイド（原文・和訳・解説）

> **論文タイトル**: Language Models (Mostly) Know What They Know
> **著者**: Saurav Kadavath, Tom Conerly, Amanda Askell, ... , Jared Kaplan (Anthropic)
> **URL**: https://arxiv.org/abs/2207.05221
> **本ドキュメントの目的**: 章ごとに原文・和訳・解説を記載し、論文全体を一読で理解する
> **対象読者**: calibration / DEL の前提知識がない卒論生

---

## Abstract

### 原文

We study whether language models can evaluate the validity of their own claims and predict which questions they will be able to answer correctly. We first show that larger models are well-calibrated on diverse multiple choice and true/false questions when they are provided in the right format. Thus we can approach self-evaluation on open-ended sampling tasks by asking models to first propose answers, and then to evaluate the probability "P(True)" that their answers are correct. We find encouraging performance, calibration, and scaling for P(True) on a diverse array of tasks. Performance at self-evaluation further improves when we allow models to consider many of their own samples before predicting the validity of one specific possibility. Next, we investigate whether models can be trained to predict P(IK), the probability that "I know" the answer to a question, without reference to any particular proposed answer. Models perform well at predicting P(IK) and partially generalize across tasks, though they struggle with calibration of P(IK) on new tasks. The predicted P(IK) probabilities also increase appropriately in the presence of relevant source materials in the context, and in the presence of hints towards the solution of mathematical word problems. We hope these observations lay the groundwork for training more honest models, and for investigating how honesty generalizes to cases where models are trained on objectives other than the imitation of human writing.

### 和訳

言語モデルが「自分の主張の正しさ」を評価し、「どの質問に正しく答えられるか」を予測できるかを研究する。まず、大きなモデルは適切なフォーマットで提示された多様な選択式問題・真偽問題において、よくキャリブレーションされていることを示す。これを利用して、自由記述タスクでの自己評価に取り組む——モデルにまず回答を提案させ、次にその回答が正しい確率「P(True)」を評価させる。多様なタスクにおいて P(True) の性能・キャリブレーション・スケーリングに心強い結果を得た。さらに、一つの回答を評価する前にモデル自身の複数のサンプルを見せると、自己評価の性能が向上する。次に、特定の回答を参照せずに、モデルが「自分がその質問に答えられるか」の確率 P(IK)（"I Know"の確率）を予測するよう訓練できるかを調査する。モデルは P(IK) の予測を上手くこなし、タスク間でも部分的に汎化するが、新しいタスクでの P(IK) のキャリブレーションには苦戦する。また、P(IK) は文脈中に関連する参考資料がある場合や、数学文章題へのヒントがある場合に適切に上昇する。これらの観察が、より誠実なモデルの訓練と、人間の文章の模倣以外の目的で訓練されたモデルにおける誠実さの汎化の研究の基盤となることを期待する。

### 解説

**この論文が問うていること**:
「AIは自分が正しいかどうかを分かっているのか？」——これがこの論文の核心的な問い。

**2つの主要な実験アプローチ**:

1. **P(True) — 自己評価**
   - モデルに回答を生成させた後、「その回答は正しいか？」と聞く
   - True/False 形式で聞くと、大きいモデルほどうまく判定できる
   - さらに「自分の他の回答」を複数見せてから判定させると精度が上がる（ブレインストーミング効果）

2. **P(IK) — 自己知識**
   - 回答を見せずに「この質問に答えられると思うか？」と聞く
   - これは「世界の事実」ではなく「モデル自身の知識状態」についての質問
   - TriviaQA で訓練すると、数学やコード問題にもある程度汎化する

**あなたの研究との接続**:
- この論文の P(True) が、あなたの研究の「Verbalized Confidence」に対応する
- ECE（キャリブレーション誤差）は、この論文でも中心的な評価指標
- DEL フレーミングでは P(IK) を「負の内省公理（知らないことを知っている）」の検証と解釈できる

---

## Section 1: Introduction

### 原文

We would eventually like to train AI systems that are honest, which requires that these systems accurately and faithfully evaluate their level of confidence in their own knowledge and reasoning. So AI systems must be able to recognize what they do and do not know, as a prerequisite. In this work, we study the extent to which Language Models (LMs) possess this ability and how it can be elicited and imparted.

As a starting point, we examine calibration: do the probabilistic predictions from language models match up with frequencies of occurrence? Language models can produce well-calibrated predictions for token probabilities on-distribution. We show that large language models are also well-calibrated on a diverse array of multiple choice questions, as long as the questions are formatted appropriately. In particular, calibration improves with model size and few-shot prompting.

Good calibration opens up the possibility for using models to evaluate the accuracy of their own outputs ("self-evaluation"). For example, given any open-ended query, we can sample an answer from the model and then have the model evaluate P(True), the probability that its answer is correct. We may expect self-evaluation to be challenging, because the model may be overconfident that its own samples are correct. Our self-evaluation procedure nevertheless distinguishes correct and incorrect samples, as summarized in Figure 1. Furthermore, as model size and capabilities increase, models improve at self-evaluation, which suggests that verification improves faster than generation quality in this context.

We also show that self-evaluation can be improved if we provide a model with many of its own samples, before asking it to evaluate any single sample. That is, 'brainstorming' other possibilities helps large models to evaluate the validity of a given answer option.

These techniques address a question about the world, as they ask models to evaluate "according to accepted truth in the wider world (i.e. according to humans), is a particular answer to a question correct?" In the case of self-evaluation, the proposed answer was provided by the model, but its validity is nevertheless an external fact. But we are also interested in having language models attempt to directly evaluate their own state of knowledge. To this purpose, we investigate what happens when we train models to predict whether or not they can correctly answer questions themselves. This is really a question about the model since we are training the model to learn what sorts of questions it, in particular, can answer.

### 和訳

私たちは最終的に「誠実な」AIシステムを訓練したい。そのためにはシステムが自身の知識と推論に対する確信度を正確かつ忠実に評価する必要がある。したがって、AIシステムは「何を知っていて何を知らないか」を認識できなければならない。本研究では、言語モデル（LM）がどの程度この能力を持っているか、そしてそれをどう引き出し・付与できるかを研究する。

出発点として、キャリブレーションを調べる——言語モデルの確率的予測は、実際の発生頻度と一致するか？ 言語モデルは分布内のトークン確率について、よくキャリブレーションされた予測を生成できることが知られている。我々は、大規模言語モデルが多様な選択式問題においてもよくキャリブレーションされていることを示す（質問が適切にフォーマットされている限り）。特に、キャリブレーションはモデルサイズとfew-shotプロンプティングで改善する。

良好なキャリブレーションは、モデルが自身の出力の正確性を評価する可能性（「自己評価」）を開く。例えば、任意の自由記述の質問に対して、モデルから回答をサンプリングし、次にそのモデルに P(True)（回答が正しい確率）を評価させることができる。自己評価は困難であると予想される——モデルは自分のサンプルに対して過信する可能性があるからだ。しかし、我々の自己評価手法は正しいサンプルと誤ったサンプルを区別できる。さらに、モデルサイズと能力が増すにつれて自己評価は改善する。これは「検証は生成よりも速く改善する」ことを示唆する。

また、単一のサンプルを評価する前にモデル自身の多数のサンプルを見せると、自己評価が改善されることも示す。つまり、他の可能性を「ブレインストーミング」することが、大規模モデルの回答評価に役立つ。

これらの技術は「世界についての問い」を扱っている——「広く受け入れられた真実に照らして、ある回答は正しいか？」とモデルに尋ねているからだ。一方で、我々は言語モデルが「自分自身の知識状態」を直接評価することにも興味がある。この目的で、モデル自身が質問に正しく答えられるかどうかを予測するよう訓練する場合に何が起こるかを調査する。

### 解説

**この章のポイント**:

1. **研究の動機 = 「誠実なAI」の実現**
   - AIが「嘘をつかない」ためには、まず「自分が何を知っているか」を理解していなければならない
   - これは DEL の「内省公理」とまさに同じ発想

2. **キャリブレーション → 自己評価 という論理の流れ**
   - まず「選択式問題でモデルの確率がどれだけ正確か」を確認（キャリブレーション）
   - それが良好なら → 自分の回答を「正しい/間違い」と判定させることもできるはず
   - この論理の流れが論文全体の構成を決めている

3. **「世界の知識」vs「自己知識」の区別**（あなたの研究にとって重要）
   - P(True)：「この回答は（世界的に）正しいか？」→ 外的事実の評価
   - P(IK)：「自分はこの質問に答えられるか？」→ 自己の知識状態の評価
   - あなたの研究の Verbalized Confidence は P(True) に近い。DEL フレーミングでは P(IK) の議論が第5章で使える

4. **スケーリング則の発見**
   - モデルが大きいほどキャリブレーションが改善する → あなたの研究で 4モデル比較する理由の一つ
   - 「検証は生成より速く改善する」→ 大きいモデルほど自分の誤りを見つけやすい

---

## Section 1.1: Contributions

### 原文

**Calibration: Multiple Choice, None of the Above, and True/False**

We show that when we use a format with visible lettered answer options, large models are very well calibrated on diverse multiple choice questions (e.g. from BIG Bench, MMLU, and many other evaluations). Calibration improves with model size, and it also improves when we pass from zero-shot to few-shot evaluation.

Replacing an option with 'none of the above' reduces accuracy and calibration significantly with our models. However, our models are also well calibrated on True/False distinctions, with accuracy and calibration also increasing with model capability.

We also show that RLHF policies naively seem miscalibrated, but with a simple temperature adjustment they become fairly well-calibrated on several evaluations.

**Self-Evaluation of Model-Generated Samples, without Finetuning**

Models can self-evaluate whether their own samples are True or False, though this tends to be a more challenging task (since models tend to find their own samples more plausible). Self-evaluations are well-calibrated few-shot. Showing models many of their own T=1 samples, along with a single sample to evaluate as True/False, can significantly improve their performance.

**Finetuning to Identify the Questions Models Can Correctly Answer**

We train models with a value head to predict the probability that they can answer a question correctly, which we refer to as P(IK). We find that models trained on TriviaQA have significant power to differentiate between math, lambada, and code questions that they can answer. However, P(IK) tends to be poorly calibrated on these other distributions. We study generalization of P(IK) to the inclusion of source materials and mathematical hints. We find that P(IK) responds appropriately to sources, correct hints, and incorrect or distracting hints.

### 和訳

**キャリブレーション：選択式、「該当なし」、True/False**

アルファベットでラベル付けされた回答選択肢を見せるフォーマットを使うと、大規模モデルは多様な選択式問題（BIG Bench、MMLU 等）で非常によくキャリブレーションされていることを示す。キャリブレーションはモデルサイズで改善し、zero-shot から few-shot への移行でも改善する。

選択肢を「該当なし（none of the above）」に置き換えると、精度とキャリブレーションが大幅に低下する。一方、True/False 形式でもモデルはよくキャリブレーションされており、精度とキャリブレーションはモデル能力の向上とともに改善する。

RLHF ポリシーは素朴にはキャリブレーションが悪いように見えるが、単純な温度調整で複数の評価において概ね良好なキャリブレーションになる。

**ファインチューニングなしでのモデル生成サンプルの自己評価**

モデルは自身のサンプルが True か False かを自己評価できるが、これはより困難なタスクである（モデルは自分のサンプルをより尤もらしいと感じる傾向があるため）。自己評価は few-shot でよくキャリブレーションされる。T=1 の自己サンプルを複数見せてから1つを評価させると、性能が大幅に向上する。

**モデルが正しく答えられる質問の特定のためのファインチューニング**

value head を追加して、質問に正しく答えられる確率 P(IK) を予測するようモデルを訓練する。TriviaQA で訓練されたモデルは、数学・Lambada・コード問題のうち答えられるものとそうでないものを十分に区別できる。ただし、P(IK) はこれらの他の分布ではキャリブレーションが悪い傾向がある。参考資料や数学的ヒントの付加に対する P(IK) の汎化を研究し、正しいヒント・誤ったヒント・無関係なヒントに適切に反応することを確認した。

### 解説

**この論文の3大貢献を整理すると**:

| 貢献 | 手法 | ファインチューニング | あなたの研究との関連 |
|---|---|---|---|
| ① キャリブレーション測定 | 選択式・True/False で確率を測定 | なし | ECE 計測の方法論をそのまま参考にできる |
| ② P(True) 自己評価 | 回答を生成→「正しい？」と聞く | なし（few-shot） | あなたの Verbalized Confidence の直接的なベースライン |
| ③ P(IK) 訓練 | value head を追加して訓練 | あり | あなたの研究スコープ外だが、DEL 考察で言及できる |

**重要な発見**:
- 「none of the above（該当なし）」を入れると性能が大きく下がる → モデルは「否定」が苦手
- RLHF（人間フィードバック強化学習）後のモデルはキャリブレーションが狂うが、temperature 調整で直る
- 自分のサンプルを複数見せる（ブレインストーミング）と自己評価が改善する

---

## Section 1.2: Models and Evaluation Tasks

### 原文

Our goal in this study is to evaluate calibration and generalization on a diverse range of tasks. As such we include all of the multiple choice evaluations in BIG Bench, the MMLU evaluation, TruthfulQA, LogiQA, and QuALITY. We are most interested in open-ended generation, so we study the sampling-based evaluations TriviaQA, Lambada, the Codex HumanEval, GSM8k, some basic arithmetic problems, and a dataset of additional web-scraped Python function synthesis problems.

We study a series of language models with 800M, 3B, 12B, 52B parameters. We do not include smaller models because they perform poorly on many of the evaluations we consider. The architecture and training setup for these models is identical to that in [Bai et al., 2022], except that the models we consider here were pretrained for 850B tokens, rather than the 400B tokens used in that work.

### 和訳

本研究の目標は多様なタスクでキャリブレーションと汎化を評価することである。そこで BIG Bench の全選択式評価、MMLU、TruthfulQA、LogiQA、QuALITY を含める。最も関心があるのは自由記述生成なので、サンプリングベースの評価として TriviaQA、Lambada、Codex HumanEval、GSM8k、基本的な算術問題、および GitHub からスクレイピングした Python 関数合成問題を研究する。

8億、30億、120億、520億パラメータの一連の言語モデルを研究する。多くの評価で性能が低いため、より小さいモデルは含めない。

### 解説

**使用モデルとタスクの整理**:

| カテゴリ | タスク | 形式 |
|---|---|---|
| 選択式 | BIG Bench, MMLU, TruthfulQA, LogiQA, QuALITY | 選択肢から選ぶ |
| 自由記述（短答） | TriviaQA, Lambada, 算術 | テキストで答える |
| 自由記述（長文） | Codex HumanEval, GSM8k, Python関数合成 | コードや推論を書く |

**モデルサイズ**: 800M → 3B → 12B → 52B の4段階
- あなたの研究では GPT-5 / Claude / Gemini / Swallow の「モデル種類」で比較する
- この論文は「同一アーキテクチャの異なるサイズ」で比較する → スケーリングの傾向が見える

---

## Section 1.3: Related Work

### 原文

Calibration for general ML predictions, and interventions to improve calibration, have been studied for some time. Calibration for language models and QA has also been studied, but typically it has been found that to achieve good calibration predictions must be adjusted. Selective prediction, where models abstain from answering certain questions, has been studied as well. Recently, the calibration of a wide range of models was analyzed on the diverse BIG Bench suite of tasks, where it was shown that language model calibration improves with model size.

Truthfulness has been a recent focus of various works, including benchmarks and the incorporation of web search and citation into language models. That said, truthfulness focuses primarily on factual accuracy "in the world", rather than on self-knowledge, or eliciting latent knowledge. We use "honesty" as an umbrella term for ideas including truthfulness, calibration, self-knowledge, explainability, and non-deceptiveness.

Perhaps the work most similar to ours is [Mielke et al., 2020], which is a very interesting application of metacognition/self-evaluation to improve natural language calibration. Another quite similar work is the very recent [Lin et al., 2022], where the authors train language models to express their calibration on arithmetic in words, and also study a signal analogous to P(True).

### 和訳

一般的な ML 予測のキャリブレーションとその改善介入は以前から研究されてきた。言語モデルと QA のキャリブレーションも研究されているが、良好なキャリブレーションを達成するには予測の調整が必要であることが一般的に見出されてきた。モデルが特定の質問への回答を控える「選択的予測」も研究されている。最近、多様な BIG Bench タスクにおいて、言語モデルのキャリブレーションがモデルサイズとともに改善することが示された。

真実性（Truthfulness）は最近の様々な研究の焦点であり、ベンチマークやウェブ検索・引用の言語モデルへの組み込みを含む。ただし真実性は主に「世界における」事実的正確さに焦点を当てており、自己知識や潜在知識の引き出しには焦点を当てていない。我々は「誠実さ（honesty）」を、真実性・キャリブレーション・自己知識・説明可能性・非欺瞞性を含む包括的用語として使用する。

本研究に最も類似する研究は Mielke et al., 2020（メタ認知/自己評価を自然言語キャリブレーション改善に応用）と Lin et al., 2022（算術のキャリブレーションを言葉で表現するようモデルを訓練し、P(True) に類似したシグナルも研究）である。

### 解説

**「誠実さ（Honesty）」の5つの側面**（あなたの研究の第1章に引用できる重要な概念）:

| 側面 | 意味 | この論文の対象 |
|---|---|---|
| **Truthfulness**（真実性） | 事実的に正確な情報を提供するか | ○ |
| **Calibration**（キャリブレーション） | 確率予測が実際の頻度と一致するか | ◎（メイン） |
| **Self-knowledge**（自己知識） | 自分が何を知っているかを知っているか | ◎（メイン） |
| **Explainability**（説明可能性） | 思考過程を完全に開示するか | △ |
| **Non-deceptiveness**（非欺瞞性） | 意図的に嘘をつかないか | △ |

**あなたの論文での使い方**:
- 第1章で「LLM の誠実さには5つの側面がある（Kadavath et al., 2022）」と引用
- DEL フレーミングでは「Self-knowledge = 内省公理」と接続
- あなたの研究は Calibration と Self-knowledge の2つに焦点を当てていると位置づける

---

## Section 2: Larger Models are Calibrated on Diverse Multiple Choice Questions

### 原文

A model makes calibrated predictions if the probability it assigns to outcomes coincides with the frequency with which these outcomes actually occur. Language models are known to produce calibrated token-level probabilities. In this section we will see that language models can produce well-calibrated probabilities when they are asked to choose the correct answer from among several explicit options. We believe calibration is interesting on its own, but it is especially relevant to honesty, since a model that can produce calibrated answers to meta-questions like 'do you know the answer to X' must know something about what it knows. Generally we can use calibration as a way to bootstrap towards self-knowledge.

We find that when multiple choice problems are formatted in this way:

Question: Who was the first president of the United States?
Choices:
(A) Barack Obama
(B) George Washington
(C) Michael Jackson
Answer:

and we identify the answers only by their labels, as e.g. '(B)', our largest models tend to produce a well-calibrated probability distribution among the available options. It is crucial that the model gets to see the answer choices explicitly before choosing amongst them; without this, we would not expect a calibrated response, due to ambiguities and degeneracies among possible paraphrases. Task formatting is important for achieving excellent calibration, and calibration improves as we pass from 0-shot to 5-shot evaluation.

### 和訳

キャリブレーションされた予測とは、モデルが結果に割り当てる確率が、実際に結果が発生する頻度と一致することである。言語モデルはトークンレベルの確率についてはキャリブレーションされていることが知られている。本セクションでは、言語モデルが明示的な選択肢の中から正解を選ぶよう求められた場合にも、よくキャリブレーションされた確率を生成できることを示す。キャリブレーション自体も興味深いが、「X の答えを知っていますか？」といったメタ質問にキャリブレーションされた回答を生成できるモデルは、自身の知識について何かを知っていなければならないという点で、誠実さに特に関連がある。一般に、キャリブレーションを「自己知識へのブートストラップ」として使える。

選択式問題を上記のフォーマット（アルファベットラベル付き選択肢）で提示すると、最大モデルはよくキャリブレーションされた確率分布を生成する傾向がある。モデルが選択肢を明示的に見てから選ぶことが不可欠であり、これなしでは回答の言い換えや曖昧さによりキャリブレーションされた応答は期待できない。タスクのフォーマットが優れたキャリブレーションの達成に重要であり、0-shot から 5-shot 評価への移行でキャリブレーションは改善する。

### 解説

**この章の核心メッセージ**:
「選択式問題を正しいフォーマットで出せば、大きなモデルほどキャリブレーションが良い」

**重要な条件**:
- **(A) (B) (C) のラベル付き**フォーマットが必須
  - ラベルなしだと「Washington」vs「George Washington, the first US president」のような曖昧さが生じる
  - 各選択肢が1トークンに対応するのでモデルが確率を出しやすい
- **few-shot（数例を見せる）**でキャリブレーションが改善
- **モデルサイズが大きいほど**キャリブレーションが改善

**あなたの研究への直接的な示唆**:
- あなたのプロンプト設計（4方式比較）において、「0-100 整数」「5段階」等のフォーマットの違いがキャリブレーションに影響することを予測する根拠になる
- 「フォーマットが重要」は RQ3（プロンプト形式による差）の理論的裏付け

**キーフレーズ（引用候補）**:
> "calibration as a way to bootstrap towards self-knowledge"
> （キャリブレーションを自己知識へのブートストラップとして使う）

→ これは DEL フレーミングの序論にぴったりの引用

---

## Section 3: From Calibration to Knowing What You Know

### 3.1 Replacing an Option with 'None of the Above' Harms Performance and Calibration

#### 原文

We have seen that language models can produce calibrated probabilities for multiple choice questions, at least when the questions and choices are provided in the right format. However, to achieve this feat the model only needs to determine the relative weight for several concrete options, when they are compared to each other. We are more interested in whether the model actually knows whether each of the answer options is correct, when judged independently. To probe this question, we modified our multiple choice evaluations by replacing their final option with "none of the above".

We found that this procedure degraded performance very significantly on evaluations. Furthermore, adding "none of the above" also harms calibration. It seems that even the 52B model is biased against using the "none of the above" option and failed to use it with appropriate frequency.

#### 和訳

言語モデルが選択式問題でキャリブレーションされた確率を生成できることは見た。しかし、この成果を達成するためにモデルが必要とするのは、複数の具体的な選択肢を相互に比較したときの相対的な重みの決定のみである。我々はモデルが各選択肢の正しさを独立に判断できるかにより関心がある。この問いを検証するため、選択式評価の最後の選択肢を「該当なし（none of the above）」に置き換えた。

この手続きにより性能が非常に大幅に低下することが分かった。さらに「該当なし」の追加はキャリブレーションも損なう。520億パラメータモデルでさえ「該当なし」オプションの使用にバイアスを持ち、適切な頻度で使用できなかった。

#### 解説

**なぜ「該当なし」が難しいのか**:
- 普通の選択式：「AとBとCを比べて、一番正しそうなのを選ぶ」→ 相対評価でOK
- 「該当なし」付き：「A, B, C のどれも正しくない可能性もある」→ **絶対評価**が必要
- モデルは「目の前にある具体的な選択肢を比較する」ことは得意だが、「どれも違う」と判断するのは苦手

**DEL との接続**:
- これは「負の内省公理（¬K φ → K ¬K φ）」の困難さに対応する
- 「答えを知らない」と認識すること = 「none of the above」を選ぶこと
- **モデルはこれが苦手** → DEL の観点から「負の内省が不完全」と解釈できる

---

### 3.2 Models are Well-Calibrated on True/False Tasks

#### 原文

Here we take a different approach, and simply ask models if a given answer is true or false. So we use the format:

Question: Who was the first president of the United States?
Proposed Answer: George Washington
Is the proposed answer:
(A) True
(B) False
The proposed answer is:

If the model responses are correct at more than chance level, and especially if they are calibrated, then the probability P(True) indicates whether the model believes a response is valid. As a first test, we can use answer options from existing multiple choice tasks. We see that the 52B model is quite well-calibrated in this context.

#### 和訳

ここでは別のアプローチを取り、与えられた回答が正しいか間違っているかを単純にモデルに尋ねる。上記のフォーマット（True/False 形式）を使用する。

モデルの応答がチャンスレベルを上回って正しく、特にキャリブレーションされていれば、P(True) の確率は「モデルがその回答を正当と信じているか」を示す。最初のテストとして、既存の選択式タスクの回答選択肢を使用した。520億パラメータモデルはこの文脈でかなりよくキャリブレーションされている。

#### 解説

**True/False 形式がこの論文の鍵**:
- 「none of the above」は難しかった → じゃあ「正しい？間違い？」と直接聞こう
- この True/False 形式が Section 4 の自己評価（P(True)）の基盤になる
- **あなたの研究の Verbalized Confidence もこの考え方の延長線上にある**

---

### 3.3 RLHF Policy Miscalibration Can Be Remediated with a Temperature Tuning

#### 原文

We also looked at calibration for a helpful and harmless RLHF policy. We find that these policies naively appear very miscalibrated, which is not surprising, since RL finetuning tends to collapse language model predictions towards behaviors that receive the most reward. However, a simple temperature adjustment (with the same temperature T=2.5 for all evaluations) largely fixes calibration issues with several independent evaluation tasks.

#### 和訳

RLHF（人間のフィードバックによる強化学習）ポリシーのキャリブレーションも調べた。これらのポリシーは素朴にはキャリブレーション不良に見えるが、これは驚くべきことではない——RL ファインチューニングは言語モデルの予測を最も報酬の高い行動に集中させる傾向があるからだ。しかし、温度パラメータの単純な調整（全評価で同一の T=2.5）により、複数の独立した評価タスクでキャリブレーション問題が概ね解消された。

#### 解説

**RLHF とキャリブレーションの関係**（あなたの研究に重要）:
- GPT-5, Claude, Gemini は全て RLHF（または類似手法）で訓練されている
- つまり、**あなたが実験するモデルは全て RLHF 済み**
- この論文によれば RLHF 後のモデルはキャリブレーションが悪くなるが、temperature 調整で改善可能
- **示唆**: あなたの実験設計で temperature パラメータの設定が重要。デフォルト値（通常 T=1）で測定するか、調整するかは方法論として明記すべき

---

## Section 4: Ask the AI: Is your proposed answer True or False?

### 4.1 Basic Self-Evaluation

#### 原文

We will now apply the True/False approach from section 3.2 to the samples models generated when trying to answer questions, including the short answer tasks arithmetic, Lambada, and TriviaQA, and the long-form answer tasks Codex HumanEval and GSM8k. In almost all cases self-evaluation performance improves with model size, and for our 52B models answers labeled with P(True) > 50% are far more likely to be correct as compared to generic responses.

In section 3.2 we saw that large language models are well-calibrated on True/False questions. Our primary motivation for studying this issue was to ask language models about their own outputs. That is, we are interested in a process where we first ask a question, sample a response from the model, then ask the model about its own sample:

Question: Who was the first president of the United States?
Proposed Answer: George Washington was the first president.
Is the proposed answer:
(A) True
(B) False
The proposed answer is:

This True/False self-evaluation may be considerably more difficult than the tasks we studied in section 3.2, because there the model was presented with human-written possibilities, whereas here the model is forced to evaluate its own samples. These samples may lie close to the model's own decision boundary for validity, or the model may simply be overconfident about its own samples.

#### 和訳

Section 3.2 の True/False アプローチを、モデルが質問に答えようとしたときに生成したサンプルに適用する。短答タスク（算術、Lambada、TriviaQA）と長文回答タスク（Codex HumanEval、GSM8k）を含む。ほぼ全てのケースで自己評価性能はモデルサイズとともに改善し、520億パラメータモデルでは P(True) > 50% とラベル付けされた回答は一般的な応答に比べてはるかに正しい可能性が高い。

この True/False 自己評価は Section 3.2 で研究したタスクよりかなり困難かもしれない。なぜなら Section 3.2 では人間が書いた候補をモデルに提示していたが、ここではモデルは自分自身のサンプルを評価しなければならないからだ。これらのサンプルはモデル自身の正当性の判断境界付近にある可能性があり、またモデルは自分のサンプルに対して過信しているかもしれない。

#### 解説

**自己評価の核心的な難しさ**:
- 人間が書いた「バラク・オバマ」を「間違い」と判定するのは簡単
- でも**自分が書いた回答**を「間違い」と判定するのは難しい
  - 理由1: 自分の回答は「もっともらしく」生成されているので、判断境界付近にある
  - 理由2: モデルが自分の出力を過信する傾向がある（過信バイアス）

**この構造はあなたの研究そのもの**:
- あなたの実験は「モデルに回答させて、同時に確信度を言わせる」
- つまり P(True) の自己評価と同じ構造
- **あなたの研究では P(True) を「確信度を0-100で明示させる」形式に変えている**のが違い

---

### 4.2 Showing Many T=1 Samples Improves Self-Evaluation

#### 原文

We can improve performance further by showing the model other T=1 samples, for comparison. That is, we generate 5 samples in total, and then ask the model about the validity of one of these samples:

Question: Who was the third president of the United States?
Here are some brainstormed ideas: James Monroe / Thomas Jefferson / John Adams / Thomas Jefferson / George Washington
Possible Answer: James Monroe
Is the possible answer:
(A) True
(B) False
The possible answer is:

With this format, performance improves significantly on all of the short-form answer tasks, as compared to the version where we only show models a single proposed answer. However, models benefit less from this approach on tasks requiring long-form answers (Codex and GSM8k).

A pragmatic comparison of self-evaluation techniques can be seen on the bottom of Figure 11. There we directly compare the overall accuracy of our models at the task, to the accuracies for the subset of responses where the models chose P(True) > 0.5. We see that these conditional accuracies are substantially higher than the overall accuracy, with the separation between base and conditional accuracies growing with model size. This suggests that as capabilities improve and samples become more sophisticated, models seem to demonstrate relative improvement at self-evaluation, compared to their generative ability. This accords with the intuitive sense that verification is often easier than generation.

#### 和訳

他の T=1 サンプルをモデルに見せて比較させることで、さらに性能を改善できる。5つのサンプルを合計で生成し、そのうち1つの妥当性についてモデルに尋ねる（上記のブレインストーミング形式）。

このフォーマットにより、単一の提案回答のみを見せる場合と比較して、全ての短答タスクで性能が大幅に改善する。ただし、長文回答タスク（Codex や GSM8k）ではこのアプローチの恩恵は小さい。

Figure 11 の下部では、タスク全体での精度と、モデルが P(True) > 0.5 を選んだ応答サブセットの精度を直接比較している。条件付き精度は全体精度よりも大幅に高く、基準精度と条件付き精度の差はモデルサイズとともに拡大する。これは能力が向上しサンプルがより洗練されるにつれて、モデルが生成能力に対して自己評価で相対的な改善を示すことを示唆する。これは「検証は生成よりも容易である」という直感的な感覚と一致する。

#### 解説

**ブレインストーミング効果（重要な知見）**:

「他の候補を見てから判断させると正確になる」のは日常感覚でも分かる。

- 1つの答えだけ見て「正しい？」→ 判断材料が少ない
- 5つの候補を見てから「この中でどれが正しい？」→ 比較できるので精度が上がる

**「検証 > 生成」の法則**:
> "verification is often easier than generation"

これは重要なキーフレーズ。大きなモデルほど:
- 生成の質も上がるが
- 自己評価の質はもっと速く上がる
- つまり「答えを出す能力」より「答えを検証する能力」の方が速く成長する

**あなたの研究への示唆**:
- 4モデル比較で「大きい/新しいモデルほどキャリブレーションが良い」傾向が見えれば、この「検証 > 生成」法則の再現になる
- 逆に日本語特化モデル（Swallow）が英語モデルよりキャリブレーションが悪ければ、「能力が低いと自己評価も低い」の傍証

---

## Section 5: Training Models to Predict Whether They Can Answer Questions Correctly

### 5.1 Evaluating P(IK) Training and Model Size Trends

#### 原文

In this section, we will train models to predict whether they know the answer to any given free-form question, denoting the probability they assign as P(IK) (for Probability that I Know the answer). This is fundamentally a question about the model itself, as different models will know the answers to different questions. We considered two approaches:

Value Head: We train P(IK) as the logit from an additional value 'head' added to the model (independent of the logits for language modeling).

Natural Language: We train P(IK) by asking the model to literally address "With what confidence could you answer this question?", and output an answer like 0%, 10%, 20%, ... 100%.

For each question, we generated 30 answer samples at T=1. For a given question Q, if 20 of the model's sampled answers were correct, and 10 were incorrect, our training set contained 20 copies of the (Q, IK) datapoint and 10 copies of the (Q, IDK) datapoint. We finetuned the entire model along with the value head.

In Figure 12, we evaluate this classifier on a held-out set of TriviaQA test questions, and see that the model is able to separate the questions it got correct and incorrect quite well. In particular, P(IK) is very well calibrated on TriviaQA.

#### 和訳

本セクションでは、モデルが任意の自由形式の質問に対して答えを知っているかどうかを予測するよう訓練する。モデルが割り当てる確率を P(IK)（"I Know" の確率）と表記する。これは根本的にモデル自身についての問いである——異なるモデルは異なる質問の答えを知っているからだ。2つのアプローチを検討した:

Value Head: モデルに追加の value「ヘッド」を付け、そのロジットとして P(IK) を訓練する（言語モデリングのロジットとは独立）。

自然言語: 「この質問にどの程度の確信を持って答えられますか？」と文字通りモデルに尋ね、0%, 10%, 20%, ... 100% のような回答を出力させる。

各質問に対して T=1 で30個の回答サンプルを生成した。ある質問 Q に対してモデルのサンプル回答のうち20個が正解、10個が不正解だった場合、訓練セットには (Q, IK) のデータポイント20個と (Q, IDK) のデータポイント10個が含まれる。value head とともにモデル全体をファインチューニングした。

TriviaQA のテスト問題の保留セットで評価すると、モデルは正解できる質問とできない質問を非常によく分離できた。特に P(IK) は TriviaQA 上で非常によくキャリブレーションされている。

#### 解説

**P(IK) の核心**:

P(True)は「この具体的な回答は正しいか？」と聞く → **回答ありき**の評価
P(IK)は「この質問に答えられるか？」と聞く → **回答なし**で自己知識を問う

**訓練データの作り方が賢い**:
1. 質問を1つ選ぶ
2. その質問に30回答えさせる（T=1 でランダムサンプリング）
3. 正解率 = Ground Truth P(IK)（例: 20/30 = 66.7%）
4. この正解率をラベルとして、P(IK) を予測するヘッドを訓練する

**「自然言語アプローチ」はあなたの研究そのもの**:
- この論文では Natural Language アプローチ（「何%の確信で答えられる？」と聞く方法）は初期実験で大きなメリットが見えなかったため、Value Head に移行した
- しかし、**あなたの研究はまさにこの Natural Language アプローチを正面から扱う**
- つまりこの論文が「将来の研究として残した課題」にあなたの研究が答えるという構図

---

### 5.2 Out of Distribution Generalization of P(IK)

#### 原文

Next, we study the generalization of P(IK) when training only on TriviaQA and then evaluating on Lambada, Arithmetic, GSM8k, Codex HumanEval, and a set of naturally occurring python function synthesis tasks scraped from GitHub. We are interested in how generalization scales across model sizes, and how performance compares to the case where we do train P(IK) on these distributions.

We see that generalization gets better as model size increases. There is a general trend where the AUROC of P(IK) increases with model size, and calibration gets better with model size. However, when testing on Lambada, calibration was terrible, because the model produces uniformly low P(IK) scores. Training on all 4 tasks resolves this issue. Even when we only train on TriviaQA, we see decent generalization to other tasks. However, training on everything does help across all tasks.

#### 和訳

次に、TriviaQA のみで訓練し、Lambada、算術、GSM8k、Codex HumanEval、GitHub からスクレイピングした Python 関数合成タスクで評価した場合の P(IK) の汎化を研究する。

モデルサイズが大きくなるにつれて汎化が良くなることが見える。P(IK) の AUROC はモデルサイズとともに増加し、キャリブレーションもモデルサイズで改善する一般的傾向がある。しかし Lambada でテストするとキャリブレーションは酷く、モデルが一様に低い P(IK) スコアを出すためである。4タスク全てで訓練するとこの問題は解消される。TriviaQA のみで訓練しても他タスクへのまずまずの汎化が見られるが、全タスクで訓練する方が全タスクで改善する。

#### 解説

**汎化（Generalization）の意味**:
- TriviaQA（雑学クイズ）で「自分が答えられるか判断する」ことを学んだモデルが、数学やコードの問題でもある程度「自分が答えられるか」を判断できるか？
- → **部分的にはできる**。ただしキャリブレーション（確率の精度）は分布外で悪くなる

**Table 1 の数値（重要）**:

| タスク | TriviaQA のみで訓練 AUROC | 全タスクで訓練 AUROC |
|---|---|---|
| TriviaQA | 0.864 | 0.873 |
| 算術 | 0.928 | 0.987 |
| LAMBADA | 0.606 | 0.853 |
| Python関数合成 | 0.687 | 0.881 |
| GSM8k | 0.624 | 0.752 |

→ AUROC が高いほど「知っている問題と知らない問題を区別できる」

**あなたの研究への示唆**:
- 4ドメイン（常識・数学・歴史・翻訳）でキャリブレーションに差が出ることは、この論文の汎化結果と整合する
- 特に翻訳は他ドメインとの距離が大きいので、キャリブレーション差が出やすいと予測できる

---

### 5.3 P(IK) Generalizes to Account for Source Materials

#### 原文

If we consider a fairly obscure question like "What state's rodeo hall of fame was established in 2013?" then P(IK) appropriately predicts a low value, specifically 18% for a 52B model. However, if we prepend a Wikipedia article on the Idaho Rodeo Hall of Fame to the context, then the P(IK) score rises to 78%. In other words, without any further training, P(IK) generalizes to address whether the language model can find answers to questions in source materials within its context.

We demonstrate this phenomenon quantitatively using questions from TriviaQA, by comparing P(IK) evaluated both with and without accompanying reference material. We see that including the article increases P(IK). Furthermore, shorter articles increase P(IK) more. Presumably this is because the correct answer is easier to extract from shorter articles than longer articles.

#### 和訳

かなりマイナーな質問「何州のロデオの殿堂が2013年に設立されたか？」を考えると、P(IK) は適切に低い値（520億パラメータモデルで18%）を予測する。しかし、アイダホ州ロデオ殿堂のウィキペディア記事を文脈に付け加えると、P(IK) スコアは78%に上昇する。つまり追加の訓練なしに、P(IK) は「言語モデルが文脈内の参考資料から回答を見つけられるかどうか」に汎化する。

TriviaQA の質問を使って、参考資料の有無で P(IK) を比較してこの現象を定量的に示す。記事を含めると P(IK) が増加する。さらに短い記事の方が P(IK) をより多く増加させる。おそらく短い記事からの方が正解を抽出しやすいためである。

#### 解説

**これは驚くべき発見**:
- P(IK) は「素の質問に答えられるか」だけを訓練された
- なのに「参考資料を渡すと P(IK) が上がる」ことを自発的に学んだ
- これは「文脈中に答えがある → 答えられる確率が上がる」をモデルが理解していることを意味する

**DEL との接続（重要）**:
- DEL では `[!φ]ψ`（公共発表 φ の後にψが成り立つ）= 情報更新
- 参考資料を渡す = 情報更新 → P(IK) が上昇 = エージェントの知識が更新される
- **あなたの第5章（考察）で「P(IK) の参考資料への汎化は DEL の動的更新公理と対応する」と議論できる**

---

### 5.4 P(IK) Generalizes to Account for Hints Towards GSM8k Solutions

#### 原文

In this section we study how hints towards the solution of GSM8k problems affect P(IK) scores. We see that (1) showing more of the hint generally leads to higher P(IK), (2) good hints that lead to the correct answer result in higher P(IK) scores than bad hints, and (3) the P(IK) model that was trained on TriviaQA, LAMBADA, Arithmetic, and Python Function Synthesis performs better and more consistently, especially with partial hints.

#### 和訳

GSM8k 問題の解法へのヒントが P(IK) スコアにどう影響するかを研究する。(1) ヒントをより多く見せるほど一般に P(IK) が高くなり、(2) 正解に導く良いヒントは悪いヒントより高い P(IK) スコアをもたらし、(3) 4タスクで訓練した P(IK) モデルの方が、特に部分的なヒントに対してより良く一貫した性能を示す。

#### 解説

ヒントが「正しいか間違いか」で P(IK) が変わるということは:
- モデルは「もらったヒントの質」を何らかの形で評価している
- 間違ったヒントでも P(IK) がある程度上がる（部分的に騙される）
- 無関係なヒント（他の問題のヒント）では P(IK) がむしろ下がる

**あなたの実験への示唆**:
- few-shot プロンプト（例題を見せてから質問）を使う場合、「例題の質」がキャリブレーションに影響する可能性がある

---

### 5.5 Comparing Models Trained with Distinct Pretraining Distributions

#### 原文

We would like P(IK) to truly capture model self-knowledge. Thus we would like to distinguish between this and an alternative hypothesis, that P(IK) is merely capturing something like the intrinsic difficulty of tasks. In order to try to disentangle these explanations, we studied two 12B models (with identical architecture) that were pretrained on distinct data distributions. We refer to these pretrained language models as A and B.

Table 2 shows that each model has a noticeably higher P(IK) for the questions that they get correct, compared to the questions that the other model gets right. The differences between the distributions are small but noticeable.

#### 和訳

P(IK) が本当にモデルの自己知識を捉えているかを確認したい。「P(IK) は単にタスクの固有の難易度を捉えているだけ」という代替仮説と区別したい。この説明を切り分けるため、同一アーキテクチャだが異なるデータ分布で事前訓練した2つの120億パラメータモデル（A と B）を研究した。

各モデルは自身が正解する質問に対して、他方のモデルが正解する質問よりも顕著に高い P(IK) を持つ。分布間の差は小さいが目に見える。

#### 解説

**この実験は「P(IK) は本当に "自分" の知識を測っているのか？」を問うている**:

- もし P(IK) が「この質問は一般的に難しいか」を測っているだけなら → モデル A と B で差は出ない
- もし P(IK) が「このモデル特有の知識」を測っているなら → A が知っていて B が知らない問題で差が出るはず
- **結果: 小さいが有意な差が出た**（Table 2）

| | A だけ正解した問題 | B だけ正解した問題 |
|---|---|---|
| A の P(IK) | **0.463** | 0.409 |
| B の P(IK) | 0.408 | **0.477** |

→ 各モデルは「自分が答えられる問題」をわずかに高い P(IK) で予測する

**結論**: P(IK) は部分的に自己知識を捉えているが、完全ではない。
**DEL 的解釈**: モデルの内省能力（K_a φ → K_a K_a φ）は不完全だが、存在する。

---

## Section 6: Discussion

### 原文

The long-term motivation underlying this work is to begin to understand aspects of honesty in AI models. We use honesty as an umbrella term including several overlapping ideas: Truthfulness, Calibration, Self-knowledge, Explainability, Non-deceptiveness.

Here we have focused on aspects of calibration, self-knowledge, and truthfulness. Our core findings are that large language models can be well-calibrated on diverse multiple choice questions, that they perform well at self-evaluation on a range of subjects, and that they can be trained to predict what they do and don't know and exhibit some generalization to new domains and in-context information sources. We found that calibration tends to improve with model size/capability and with additional few-shot examples. Self-evaluation also improves with model size, which is non-trivial since we expect the quality of model samples to also be improving as we scale up. This means that in effect, we are observing that verification has an advantage over generation.

Another motivation for this work was to use self-knowledge as a test-bed for generalization. We are particularly interested in how honesty generalizes from easy to hard questions and across domains, because we are worried about how AI systems may behave out-of-distribution, or when they have some knowledge or insight that humans lack. We found that language models do exhibit a degree of generalization across domains, though calibration suffers out-of-distribution.

### 和訳

この研究の長期的な動機は、AIモデルにおける誠実さの諸側面の理解を始めることである。誠実さを、真実性・キャリブレーション・自己知識・説明可能性・非欺瞞性という複数の重なり合う概念を含む包括的用語として使用する。

ここではキャリブレーション・自己知識・真実性の側面に焦点を当てた。我々の核心的な発見は、大規模言語モデルが多様な選択式問題でよくキャリブレーションされること、様々な主題での自己評価が優れていること、そして自分が何を知っていて何を知らないかを予測するよう訓練でき、新しいドメインや文脈内情報源への汎化も示すことである。キャリブレーションはモデルサイズ/能力と追加のfew-shot例で改善する傾向がある。自己評価もモデルサイズとともに改善し、これはモデルサンプルの質もスケールアップとともに改善するはずなので自明ではない。つまり実質的に検証が生成に対して優位であることを観察している。

もう一つの動機は、自己知識を汎化のテストベッドとして使うことだった。誠実さが簡単な問題から難しい問題へ、またドメインを横断してどう汎化するかに特に関心がある。これはAIシステムが分布外でどう振る舞うか、あるいは人間が持たない知識や洞察をAIが持つときにどう振る舞うかへの懸念と関連する。言語モデルはドメインを横断したある程度の汎化を示すが、分布外ではキャリブレーションが悪化することが分かった。

### 解説

**論文全体の結論を3行にまとめると**:
1. LLM は「自分の答えの正しさ」をある程度正確に判定できる（P(True)）
2. 「自分がこの問題に答えられるか」もある程度予測できる（P(IK)）
3. ただし新しいタスクではキャリブレーションが悪化する（汎化の限界）

**あなたの研究が埋めるギャップ**:
この論文が残した課題のうち、あなたの研究が直接取り組むもの:

| この論文の限界 | あなたの研究の対応 |
|---|---|
| 英語のみで実験 | **日本語**タスクで検証 |
| 自然言語アプローチは初期実験のみ | **Verbalized Confidence を正面から研究** |
| RLHF 後のキャリブレーションは簡単な調査のみ | RLHF 済みの**商用モデル**（GPT-5, Claude, Gemini）で直接測定 |
| 同一アーキテクチャの異なるサイズを比較 | **異なるアーキテクチャ**のモデルを比較（GPT vs Claude vs Gemini vs Swallow） |
| DEL との接続なし | **DEL フレーミング**で理論的に位置づけ |

---

### 6.1 Limitations and Future Work（原文抜粋と解説）

#### 原文（要約）

This work has a number of limitations:
- We have focused on pretrained language models, but models that have been finetuned for a specific purpose, such as RLHF policies, will not be so well-calibrated.
- Language model pretraining is a form of human imitation. Some of the most interesting questions about honesty concern setups where advanced AI systems 'know' something that clashes with or extends what humans know.
- This work does not address the possibility that AI systems may learn to behave deceptively.
- We only studied five sampling-based datasets, and our observations concerning capability trends and generalization were limited in power and scope.

#### 和訳

本研究にはいくつかの限界がある:
- 事前訓練された言語モデルに焦点を当てたが、RLHF ポリシーなどの特定目的でファインチューニングされたモデルはそれほどキャリブレーションされないだろう。
- 言語モデルの事前訓練は人間の模倣の一形態である。誠実さに関する最も興味深い問いは、高度なAIシステムが人間の知識と矛盾する、あるいはそれを超える知識を「知っている」場合に関係する。
- AIシステムが欺瞞的に振る舞うことを学習する可能性は扱っていない。
- 5つのサンプリングベースのデータセットのみを研究し、能力傾向と汎化に関する観察は検出力と範囲が限定的だった。

#### 解説

**あなたの論文の第2章（関連研究）と第6章（結論）で引用すべき限界**:

1. **RLHF の限界** → あなたの研究は RLHF 済みモデルを直接扱うので、この限界を部分的に解消
2. **5データセットの限界** → あなたは4ドメイン × 日本語というまったく別の軸で拡張
3. **欺瞞の可能性** → これはあなたの研究スコープ外だが、第5章の「今後の課題」で触れるとよい

---

## Appendix A-D: 要約

Appendix は技術的な詳細を扱っている。全文の精読は不要だが、あなたの研究で使う指標の定義がここにあるので、必要に応じて参照する。

### Appendix A: Metrics, Formatting Details, and P(IK) Training

**ECE の計算方法**:

$$ECE = \frac{1}{N} \sum_{i}^{N} |y_i - x_i|$$

- 予測確率を10個のビンに等分し、各ビン内の「平均予測確率」と「実際の正答率」の差の絶対値の平均
- この論文では最も確信度の高い予測のみを使用（多重選択の場合）
- **あなたの研究で ECE を計算するときは、この定義を参照して `calibration.py` と整合させること**

**Brier Score の定義**:

$$B = \frac{1}{N} \sum_{i}^{N} (p_i - c_i)^2$$

- $p_i$ = P(True)（モデルの自己評価確率）
- $c_i$ = 0（不正解）or 1（正解）
- 小さいほど良い。チャンスレベルは 0.25

**フォーマットの重要性**:
- ラベル付き選択肢（(A)(B)(C)）のフォーマットが良好なキャリブレーションに不可欠
- BIG Bench のデフォルトフォーマット（`choice: ...`形式）ではキャリブレーションが悪い

### Appendix B: Discriminating What Models Know with Entropy or Loss

P(IK) 以外の「モデルが答えを知っているか」を判別する手法:
- **サンプルの loss**: T=0 サンプルの loss が低い → 正解の可能性が高い
- **回答分布のエントロピー**: 同じ質問に200回答えさせ、回答の多様性を測定。多様性が低い（=同じ答えが多い）→ 正解の可能性が高い
- **ただし**: 大きなモデルは「正しいが多様な回答」を出せるため、エントロピーは頑健でない

### Appendix C: More P(True) Evaluation Results

- zero-shot では P(True) のキャリブレーションが悪い（50%付近に集中）
- few-shot にすると大幅に改善
- 小さいモデルのサンプルは全サイズのモデルにとって正誤判定が容易

### Appendix D: Mixed-Arithmetic and Function Synthesis Dataset Descriptions

- 算術データセット: プログラムで自動生成（1桁〜5桁の加減乗算）
- Python 関数合成: GitHub からスクレイピング。テストカバレッジのある関数を収集

---

## まとめ：あなたの研究にとってのこの論文の意味

### 引用すべきポイント（章別）

| あなたの論文の章 | Kadavath 2022 から引用すべきこと |
|---|---|
| **第1章 序論** | 「誠実さ」の5側面の定義、「calibration を self-knowledge へのブートストラップとして使う」 |
| **第2章 関連研究** | 主要な先行研究として詳述。P(True) / P(IK) の手法概要。英語中心という限界 |
| **第3章 手法** | ECE / Brier / AUROC の定義（Appendix A）、プロンプトフォーマットの重要性、few-shot の効果 |
| **第5章 考察** | 「検証 > 生成」法則、RLHF とキャリブレーションの関係、分布外での汎化の限界、自然言語アプローチの可能性 |

### 抜き出すべき数値

| 数値 | 出典 | 使い方 |
|---|---|---|
| AUROC 0.864（P(IK), TriviaQA, 52B） | Table 1 | 比較ベースライン |
| ECE の改善傾向（Figure 4） | Section 2 | モデルサイズと ECE の関係の根拠 |
| P(True) > 0.5 での条件付き精度の改善 | Figure 11 | 自己評価の有用性の根拠 |
| RLHF 後の temperature 2.5 でのキャリブレーション回復 | Section 3.3 | あなたの実験での temperature 設定の議論 |

### 引用したい原文（ページ番号は arXiv 版を参照）

> "calibration as a way to bootstrap towards self-knowledge"
> （キャリブレーションを自己知識へのブートストラップとして使う）— Section 2

> "verification has an advantage over generation"
> （検証は生成に対して優位である）— Section 4.2 / Section 6

> "We use 'honesty' as an umbrella term for ideas including truthfulness, calibration, self-knowledge, explainability, and non-deceptiveness."
> （「誠実さ」を真実性・キャリブレーション・自己知識・説明可能性・非欺瞞性を含む包括的用語として使用する）— Section 1.3

---

*このドキュメントは Kadavath et al. 2022 の全章を原文・和訳・解説で網羅した精読ガイドです。*
*あなたの研究の文献カード `kadavath_2022_language_models_know.md` の数値メモ欄は、上記の数値で埋められます。*

