# 未入手論文リスト（`research/papers/` に PDF がないもの）

> 作成日: 2026-07-13
> 目的: 研究計画書・各分析ドキュメントで引用されているが、`research/papers/` にPDFが
> 存在しない論文を洗い出す。ユーザーが入手できたら `research/papers/` に追加してください。
> （bib key は `references.bib` 記載のものを併記。ない場合は追加が必要）

## 現在 `research/papers/` にあるもの（参考・確認不要）
- Guo 2017 (ICML) — `guo17a.pdf`
- Kadavath 2022 — `2207.05221v4.pdf`
- Lin 2022 — `2205.14334v2.pdf`
- Tian 2023 — `2023.emnlp-main.330.pdf`
- Xiong 2024 — `2306.13063v2.pdf`
- Desai & Durrett 2020 — `2020.emnlp-main.21.pdf`
- Zheng 2023 (LLM-as-a-Judge) — `NeurIPS-2023-judging-llm-as-a-judge...pdf`
- Yang 2024 (Verbalized Confidence Scores) — `2412.14737v2.pdf`
- Dai 2025 (Rescaling Confidence) — `2603.09309v2.pdf`
- Xue 2025 (MlingConf) — `2025.findings-acl.129.pdf`
- Seo 2025 (ADVICE) — `2510.10913v3.pdf`
- Li/Liu 2025 (ConfTuner) — `2508.18847v2.pdf`

---

## 🔴 優先度高：主要な理論的支柱（Murphy分解・較正理論）

Murphy分解は現在「補足的な切り口」に位置づけを下げましたが、§9.3の探索的オプションとして
使う可能性がある限り、入手しておくと安心です。

| 著者・年 | タイトル | 出典 | 備考 |
|---|---|---|---|
| Murphy, A. H. (1973) | A New Vector Partition of the Probability Score | J. Applied Meteorology, 12(4), 595–600 | **arXiv非公開・1973年の古い論文**。大学図書館 or AMS Journals 契約経由でないと入手困難な可能性 |
| Bröcker, J. (2009) | Reliability, Sufficiency, and the Decomposition of Proper Scores | QJRMS 135(643) | arXiv:0806.0813 |
| Ferro, C. A. T. & Fricker, T. E. (2012) | A Bias-Corrected Decomposition of the Brier Score | QJRMS 138(668) | arXiv:1303.6182 |
| Pohle, M.-O. (2020) | The Murphy Decomposition and the Calibration-Resolution Principle | — | arXiv:2005.01835 |
| Siegert, S. (2017) | Simplifying and generalising Murphy's Brier score decomposition | QJRMS 143(703) | arXiv不明・要検索 |
| Gneiting, T. & Raftery, A. E. (2007) | Strictly Proper Scoring Rules, Prediction, and Estimation | JASA 102(477) | arXiv不明・要検索 |
| Nixon, J. et al. (2019) | Measuring Calibration in Deep Learning | CVPR Workshop 2019 | arXiv:1904.01685（要確認） |

---

## 🟡 優先度中：「なぜプロンプト設計か」防御論理の根拠（`why-prompt-design-defense.md`）

指導教員から「なぜプロンプト設計か」を問われた際の裏付けとして使っている論文群。

| タイトル | arXiv | 位置づけ |
|---|---|---|
| A Survey of Calibration Process for Black-Box LLMs | arXiv:2412.12767 | **最重要**：プロンプト設計が唯一の手段であることの根拠サーベイ |
| Influences on LLM Calibration: Response Agreement, Loss Functions, and Prompt Styles | arXiv:2501.03991 | プロンプトスタイルの影響を体系的に検証 |
| Adaptive Temperature Scaling | arXiv:2409.19817 (EMNLP 2024) | Post-hoc手法の代表例（比較対象） |
| Prior Adaptation（教師なし較正） | arXiv:2307.06713 | Post-hoc手法の一種 |
| Calibration-Aware RL (DPO/PPO) | arXiv:2601.13284 (2025) | Fine-tuning手法の代表例 |
| Calibration-Aware Fine-Tuning | arXiv:2505.01997 (2025) | Fine-tuning手法の代表例 |
| How do LLMs Compute Verbal Confidence? | arXiv:2603.17839 (2026) | 言語的確信度の自己評価性を支持 |
| Process Supervision of Confidence Margin | arXiv:2604.23333 (2026) | プロンプト設計の延長研究 |
| Evaluating Prompt Engineering Techniques for Accuracy | arXiv:2506.00072 (2025) | プロンプト工学と精度の関係 |
| Wired for Overconfidence | arXiv:2604.01457 (2025) | 過信の機構的限界（プロンプト設計の限界を認識） |
| Verbalized Confidence Triggers Self-Verification | arXiv:2506.03723 (2025) | Verb.2Sの理論的裏付け |

---

## 🟡 優先度中：正答判定・LLM-as-a-Judge 関連（翻訳ドメイン評価）

| タイトル | arXiv | 用途 |
|---|---|---|
| COMET: A Neural Framework for MT Evaluation (Rei et al. 2020) | EMNLP 2020, arXiv不明 | 翻訳ドメインの主判定指標 |
| BERTScore (Zhang et al. 2020) | ICLR 2020, arXiv不明 | 補助評価 |
| LLMs Are State-of-the-Art Evaluators of Translation Quality (Kocmi & Federmann 2023) | arXiv:2302.14520 | LLM-as-a-Judge検証 |
| GEMBA-MQM (Kocmi & Federmann 2023) | arXiv:2310.13988 | 誤り検出手法 |
| Verbosity Bias in Preference Labeling (Saito et al. 2023) | arXiv:2310.10076 | LLM-as-a-Judgeのバイアス |
| Judging the Judges: Position Bias (Shi et al. 2024) | arXiv:2406.07791 | バイアス調査 |
| Justice or Prejudice? Biases in LLM-as-a-Judge (Ye et al. 2024) | arXiv:2410.02736 | バイアス調査 |

---

## 🟢 優先度低：データセット出典論文

| タイトル | arXiv |
|---|---|
| MMLU (Hendrycks et al. 2021) | arXiv:2009.03300 |
| GSM8K (Cobbe et al. 2021) | arXiv:2110.14168 |
| MGSM (Shi et al. 2023) | arXiv:2210.03057 |
| Mitigating Bias in Calibration Error Estimation (Roelofs et al. 2022) | AISTATS 2022、arXiv不明 |
| Beyond the Final Layer: Multilingual Calibration (Zhou et al. 2025) | arXiv:2510.03136 |

## 🟢 優先度低：日本語LLM・データセット関連

| タイトル | 出典 |
|---|---|
| Swallow: Continual Pre-Training (Fujii et al. 2024) | COLM 2024（PDF: OpenReview or arXiv要確認） |
| JGLUE (Kurihara et al. 2022) | LREC 2022 |

## 🟢 優先度低：背景（ハルシネーション・社会的リスク）

| タイトル | arXiv |
|---|---|
| Survey of Hallucination in NLG (Ji et al. 2023) | arXiv:2202.03629 |
| A Survey on Hallucination in LLMs (Huang et al. 2023) | arXiv:2311.05232 |
| On the Dangers of Stochastic Parrots (Bender et al. 2021) | FAccT 2021、arXiv不明 |

## 🟢 優先度低：較正理論の基礎（現状あまり使っていない）

| タイトル | arXiv |
|---|---|
| Accurate Uncertainties for Deep Learning (Kuleshov et al. 2018) | arXiv:1807.00263 |
| Obtaining Well Calibrated Probabilities Using Bayesian Binning (Naeini et al. 2015) | AAAI 2015、arXiv不明 |
| Reducing Conversational Agents' Overconfidence (Mielke et al. 2022) | arXiv:2012.14983 |

---

## ⚪ 参考（現在の研究の主軸ではない・DEL理論フレーミング用）

DEL（動的認識論理）は過去のフレーミング案の名残で、現在の主軸（プロンプト設計による
較正性能向上）には直接必要ありません。念のため一覧化しますが、**入手の優先度は最も低い**です。

| タイトル | 出典 |
|---|---|
| Dynamic Epistemic Logic (van Ditmarsch et al. 2007) | Springer（書籍） |
| Reasoning About Knowledge (Fagin et al. 1995) | MIT Press（書籍） |
| 情報科学における論理（小野寛晰 1994） | 日本評論社（書籍・日本語） |
| Dynamic Epistemic Logic (Baltag & Renne, SEP) | オンライン無料（PDF化不要、URLのみで足りる） |
| DEL-ToM (EMNLP 2025) | aclanthology.org/2025.emnlp-main.573 |
| Epistemic Integrity in LLMs | arXiv:2411.06528 |
| Do LLMs Know What They Don't Know? Prediction Markets | arXiv:2512.16030 |

---

## 備考

- 🔴🟡🟢 は「実際に本文・スライドで根拠として引用する可能性の高さ」による優先度目安
- arXiv論文は基本的に無料で入手可能（PDFはWebブラウザで `arxiv.org/abs/XXXX.XXXXX` → Download PDF）
- 1973年のMurphy論文のような古い気象学誌の論文は、大学図書館経由のデータベース
  （AMS Journals, J-STAGE等）でないと入手できない場合がある
- 入手した論文は `research/papers/` に置き、ファイル名は既存の慣習
  （`arXivID_version.pdf` または会議略称）に合わせると管理しやすい
