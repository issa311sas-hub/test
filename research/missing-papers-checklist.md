# 未入手論文リスト（`research/papers/` に PDF がないもの）

> 作成日: 2026-07-13
> **更新: 2026-07-13** — 優先度高・中の一部（16本）がアップロードされたため反映。
> 全16本を開いてタイトル・著者を確認し、`references.bib` に正式なエントリを追加済み。
> 目的: 研究計画書・各分析ドキュメントで引用されているが、`research/papers/` にPDFが
> 存在しない論文を洗い出す。ユーザーが入手できたら `research/papers/` に追加してください。

## ✅ 新規アップロード分（2026-07-13・全て内容確認済み）

想定していたタイトルとほぼ一致していましたが、確認の過程で以下の点を補正しました。

| ファイル | 確定タイトル・著者 | 備考（想定との差分） |
|---|---|---|
| `0806.0813v2.pdf` | Bröcker, J. (2009). Reliability, Sufficiency, and the Decomposition of Proper Scores. *QJRMS* 135(643). | 想定通り |
| `2005.01835v1.pdf` | Pohle, M.-O. (2020). The Murphy Decomposition and the Calibration-Resolution Principle. | 想定通り |
| `2020.emnlp-main.213.pdf` | Rei, R. et al. (2020). COMET: A Neural Framework for MT Evaluation. *EMNLP 2020*. | 想定通り |
| `1904.09675v3.pdf` | Zhang, T. et al. (2020, ICLR). BERTScore: Evaluating Text Generation with BERT. | ⚠️ 旧チェックリストで「arXiv不明」としていたが arXiv:1904.09675 と判明 |
| `2023.eamt-1.19.pdf` | Kocmi, T. & Federmann, C. (2023, EAMT). Large Language Models Are State-of-the-Art Evaluators of Translation Quality（GEMBA）。 | 想定通り（arXiv:2302.14520 の会議版） |
| `2023.wmt-1.64.pdf` | Kocmi, T. & Federmann, C. (2023, WMT). GEMBA-MQM: Detecting Translation Quality Error Spans with GPT-4. | 想定通り（arXiv:2310.13988 の会議版） |
| `2307.06713v3.pdf` | Estienne, L. et al. Unsupervised Calibration through Prior Adaptation for Text Classification using LLMs. | 想定通り |
| `2310.10076v1.pdf` | Saito, K. et al. (2023). Verbosity Bias in Preference Labeling by Large Language Models. | 想定通り |
| `2410.02736v2.pdf` | Ye, J. et al. (2024). Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge. | 想定通り |
| `2412.12767v1.pdf` | Xie, L. et al. (Amazon, 2024). A Survey of Calibration Process for Black-Box LLMs. | 想定通り。「なぜプロンプト設計か」の中核根拠 |
| `2024.emnlp-main.1007.pdf` | Xie, J. et al. (2024, EMNLP). Calibrating Language Models with Adaptive Temperature Scaling. | ⚠️ `why-prompt-design-defense.md` では arXiv:2409.19817 とのみ記載していたが、これがEMNLP会議版と確認 |
| `2025.acl-long.188.pdf` | Xia, Y. et al. (2025, ACL). Influences on LLM Calibration: Response Agreement, Loss Functions, and Prompt Styles. | 想定通り（arXiv:2501.03991 の会議版） |
| `2025.ijcnlp-long.18.pdf` | Shi, L. et al. (2025, IJCNLP-AACL). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. | ⚠️ `answer-judgment-analysis.md` では「Shi, J. (2024) arXiv:2406.07791」としていたが、著者は **Lin Shi**、会議版は2025年 IJCNLP-AACL 掲載と判明。中身の内容（Position Bias調査）は一致 |
| `2505.01997v3.pdf` | Xiao, J. et al. Restoring Calibration for Aligned Large Language Models: A Calibration-Aware Fine-Tuning Approach. | 想定通り（"Calibration-Aware Fine-Tuning"） |
| `2506.00072v1.pdf` | Naderi, N. et al. Evaluating Prompt Engineering Techniques for Accuracy and Confidence Elicitation **in Medical LLMs**. | ⚠️ 医療LLMに特化した論文だった（想定では汎用のプロンプト工学評価と考えていた）。引用時は「医療ドメインでの実証」と明記すること |
| `2506.03723v1.pdf` | Jang, C. et al. Verbalized Confidence Triggers Self-Verification: Emergent Behavior Without Explicit Reasoning Supervision. | 想定通り |

**内容の要点（研究への関連）:**
- **Bröcker 2009 / Pohle 2020**: Murphy分解が任意のProper Scoring Ruleに一般化されることの理論的根拠。§9.3の探索的オプションの裏付けとして必要十分。
- **Xie et al. 2024 (Black-Box Survey)**: 商用LLMがlogitsを公開しないため、Post-hoc補正が原理的に使えないことを支持する最重要文献。「なぜプロンプト設計か」の中心的根拠。
- **Xia et al. 2025 (ACL)**: プロンプトスタイルが較正に与える影響を体系的に検証しており、本研究のRQ3（プロンプト方式間の比較）と直接関連。
- **Xiao et al. 2025 / Xie et al. 2024 (Adaptive Temp Scaling)**: それぞれFine-tuning系・Post-hoc系の代表例。「本研究ではプロンプト設計のみに限定する」という研究の切り分けの比較対象として使う。
- **COMET / BERTScore / GEMBA / GEMBA-MQM**: 翻訳ドメイン（FLORES-200）の正答判定方法の根拠一式。COMETが主判定、BERTScoreは補助、GEMBAはLLM-as-a-Judge検証手段。
- **Saito 2023 / Ye 2024 / Shi 2025 (Judging the Judges)**: LLM-as-a-Judge使用時のバイアス（冗長性バイアス・位置バイアス）に関する注意喚起。翻訳ドメインでLLM-as-a-Judgeを「検証手段」に留める設計判断の根拠。
- **Naderi 2025**: 医療ドメインでのプロンプト工学と確信度の関係。ドメインが異なるため直接の先行研究ではないが、プロンプト設計が確信度に影響するという傾向を補強する傍証として使える。
- **Jang 2025**: ⚠️**[2026-07-13 訂正]** 当初「Verb.2Sの理論的裏付け」としていたが誤り。この論文はLoRA fine-tuningでCoT推論に自己検証行動（再計算・言い直し）を誘発する手法であり、
  本研究のVerb.2S（プロンプトのみ・別ターンで確信度を尋ねる）とは対象も手段も異なる。H1の根拠としては使わない（詳細: `prompt-design-analysis.md` §1.7参照）。
  傍証として使うなら「確信度の言語化がモデル内部で何らかの追加処理を誘発しうる」という一般的傾向の指摘に留める。

`references.bib` に bibkey 付きで登録済み（`brocker2009reliability`, `pohle2020murphy`,
`rei2020comet`, `zhang2020bertscore`, `kocmi2023gemba`, `kocmi2023gembamqm`,
`saito2023verbosity`, `shi2025judgingjudges`, `ye2024justiceprejudice`,
`xie2024blackboxsurvey`, `xie2024adaptivetemp`, `estienne2023prioradaptation`,
`xiao2025restoringcalibration`, `xia2025influences`, `naderi2025medicalprompt`,
`jang2025verbalizedselfverify`）。

---

## 既存（以前から `research/papers/` にあるもの）
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

## 🔴 まだ未入手：Murphy分解の周辺理論（優先度高のうち残り）

| 著者・年 | タイトル | 出典 | 備考 |
|---|---|---|---|
| Murphy, A. H. (1973) | A New Vector Partition of the Probability Score | J. Applied Meteorology, 12(4), 595–600 | **arXiv非公開・1973年の古い論文**。大学図書館 or AMS Journals 契約経由でないと入手困難な可能性 |
| Ferro, C. A. T. & Fricker, T. E. (2012) | A Bias-Corrected Decomposition of the Brier Score | QJRMS 138(668) | arXiv:1303.6182 |
| Siegert, S. (2017) | Simplifying and generalising Murphy's Brier score decomposition | QJRMS 143(703) | arXiv不明・要検索 |
| Gneiting, T. & Raftery, A. E. (2007) | Strictly Proper Scoring Rules, Prediction, and Estimation | JASA 102(477) | arXiv不明・要検索 |
| Nixon, J. et al. (2019) | Measuring Calibration in Deep Learning | CVPR Workshop 2019 | arXiv:1904.01685（**1904.09675=BERTScoreとは別の論文なので注意**） |

---

## 🟡 まだ未入手：「なぜプロンプト設計か」防御論理の残り（2026年の新しい論文）

| タイトル | arXiv | 位置づけ |
|---|---|---|
| Calibration-Aware RL (DPO/PPO) | arXiv:2601.13284 (2025) | Fine-tuning手法の代表例 |
| How do LLMs Compute Verbal Confidence? | arXiv:2603.17839 (2026) | 言語的確信度の自己評価性を支持 |
| Process Supervision of Confidence Margin | arXiv:2604.23333 (2026) | プロンプト設計の延長研究 |
| Wired for Overconfidence | arXiv:2604.01457 (2025) | 過信の機構的限界（プロンプト設計の限界を認識） |

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
