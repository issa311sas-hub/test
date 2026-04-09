# 文献要約カード: Tian et al. (2023)

> **注意**: このカードは「こういう感じで埋める」という例示のための初期版。
> 実際に精読した後、各セクションを本人の言葉で書き直すこと。

---

## 基本情報

| 項目 | 内容 |
|---|---|
| **著者** | Katherine Tian, Eric Mitchell, Allan Zhou, Omar Khattab, ほか |
| **発行年** | 2023 |
| **タイトル（日本語）** | 単にキャリブレーションを問う: RLHF で微調整された言語モデルから校正された確信度スコアを引き出すための戦略 |
| **タイトル（原題）** | Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback |
| **掲載誌/学会** | EMNLP 2023 |
| **DOI / URL** | https://arxiv.org/abs/2305.14975 |
| **BibTeX キー** | `tian2023justask` |
| **読んだ日** | 2026-04-XX（予定） |
| **重要度** | ★★★（本研究の zero-shot 方法論の根拠） |

---

## 内容要約

### 研究目的・問い（RQ）
RLHF で微調整された LLM に対し、**プロンプトだけで** verbalized confidence を
引き出した場合、それは内部の softmax 確率（token logprob）より **良い calibration**
を示すのか？またどのような「聞き方」が最も効果的か？

### 研究方法
- **対象モデル**: GPT-3.5, GPT-4, LLaMA-2-Chat など（RLHF モデル中心）
- **タスク**: TriviaQA, SciQ, TruthfulQA 等の QA タスク
- **検討する方式**:
  - `logprob`: 生成された answer token の対数確率を使う（従来手法）
  - `linguistic`: "How confident are you?" と言語で聞く
  - `verbal numeric`: "Give a confidence score from 0 to 100"
  - `top-k`: 複数の答え候補と各々の確率を一度に出させる
- **分析**: ECE, Brier, AUROC で各方式を比較

### 主な結果
1. **RLHF 済みモデルでは、logprob ベースの calibration は崩壊している**
   - RLHF が softmax を歪めるため
2. **Verbalized confidence は logprob より calibration が良好**
   - 特に「0-100 の整数で答える」方式が強い
3. **top-k 方式（複数候補同時列挙）がさらに良い結果を示す**
4. プロンプト工夫の効果は GPT-4 で特に顕著

### 結論・主張
「単にキャリブレーションを問う」だけで、特別な fine-tuning も post-hoc calibration も
不要なレベルで calibrated な確信度を得られる。これは RLHF が softmax 確率を破壊する
一方で、モデルの「自己評価能力」自体は生きていることを示唆する。

### 研究の限界
- 英語 QA タスクのみ（日本語など未検証）
- verbal fine-tuning との組み合わせ効果は未検証
- chain-of-thought と confidence の相互作用は限定的にしか論じられていない

---

## 自分の研究との関連

### この研究が自分の卒論に役立つ点
- **zero-shot で verbalized confidence を使う方法論の直接的な根拠**
- 本研究のプロンプト比較（実験2）の設計根拠
- 「logprob はもう信用できないので verbalized で行く」という主張の出典
- 特に 0-100 整数方式を採用している本研究の理由付けに引用

### 自分の研究との違い・差別化ポイント

| 観点 | Tian et al. (2023) | 本研究 |
|---|---|---|
| 対象言語 | 英語 | **日本語中心** |
| 対象タスク | TriviaQA 等 QA | **常識・数学・歴史・翻訳** |
| モデル | GPT-3.5/4, LLaMA-2 | **GPT-5/Claude/Gemini/Swallow** |
| プロンプト方式 | 4方式（top-k 含む） | 4方式（top-k は対象外） |
| 言語比較 | なし | **日英並行評価** |

**差別化の主張**:
1. Tian らの結果は英語のみで、日本語 LLM が同じ傾向を示すかは未検証
2. 日本語特化モデル（Swallow）で RLHF の影響がどう出るかは本研究で初めて検証
3. top-k 方式は本研究では扱わないが、将来課題として言及

### 引用予定の章
- 第1章 序論（verbalized confidence の普及を説明する際）
- **第2章 関連研究 2.2.3（本研究方法論の根拠として詳細紹介）**
- **第3章 研究方法 3.4（プロンプト設計の根拠）**
- 第5章 考察 5.2.3（本研究結果との対比）
- 第6章 結論（top-k 方式を将来課題として言及）

---

## メモ・気になったこと

- タイトル「Just Ask for Calibration」は印象的なキャッチフレーズ。
  日本語要旨で「単に聞けば良い」と紹介すると伝わりやすい
- top-k 方式は本研究では実装しなかったが、指導教員から「なぜやらないか」と
  聞かれる可能性がある → API コスト・実装難度・公平性（他方式とのサンプリング回数差）
  で説明する準備をしておく
- Tian の結果を日本語で追試するという位置付けにすると新規性が明確になる

---

## 直接引用候補

```
[精読後に埋める]
- p. XX 結論:「We find that asking the model... consistently outperforms...」
- 各プロンプト方式の具体的な文言
- ECE の具体的な数値（本研究との対比用）
```

---

## 関連論文（要チェック）

- Lin et al. (2022): Teaching Models to Express Their Uncertainty in Words
- Xiong et al. (2024): Can LLMs Express Their Uncertainty?
- Kadavath et al. (2022): Language Models (Mostly) Know What They Know
