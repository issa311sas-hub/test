# 先行研究リスト（第1版）

> **作成日**: 2026年4月9日
> **テーマ**: LLMの自己評価能力 / 日本語 Calibration
> **目標**: 最終的に30本以上。本リストは初期シード15本＋日本語LLM評価系の追加予定

---

## A. Confidence Calibration 基礎

### A-1
- **著者**: Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q.
- **年**: 2017
- **タイトル**: On Calibration of Modern Neural Networks
- **掲載**: ICML 2017
- **URL**: https://arxiv.org/abs/1706.04599
- **一言**: 深層ニューラルネットワークが過信傾向にあることを示した古典的論文。ECE（Expected Calibration Error）を普及させた。
- **本研究との関連**: 本研究の評価指標 ECE の出典。

### A-2
- **著者**: Desai, S., & Durrett, G.
- **年**: 2020
- **タイトル**: Calibration of Pre-trained Transformers
- **掲載**: EMNLP 2020
- **URL**: https://arxiv.org/abs/2003.07892
- **一言**: BERT 等の事前学習モデルの calibration を体系的に検証。
- **本研究との関連**: 伝統的 PLM の知見。LLM時代の変化を論じる基盤。

### A-3
- **著者**: Kuleshov, V., Fenner, N., & Ermon, S.
- **年**: 2018
- **タイトル**: Accurate Uncertainties for Deep Learning Using Calibrated Regression
- **掲載**: ICML 2018
- **URL**: https://arxiv.org/abs/1807.00263
- **一言**: 回帰タスクでの calibration 手法。
- **本研究との関連**: 分類以外の calibration 知見。

### A-4
- **著者**: Naeini, M. P., Cooper, G., & Hauskrecht, M.
- **年**: 2015
- **タイトル**: Obtaining Well Calibrated Probabilities Using Bayesian Binning
- **掲載**: AAAI 2015
- **一言**: ECE の具体的な計算法の根拠。
- **本研究との関連**: 実装上の基礎文献。

---

## B. LLMの自己評価能力（核心文献）

### B-1 ⭐重要
- **著者**: Kadavath, S., Conerly, T., Askell, A., et al.
- **年**: 2022
- **タイトル**: Language Models (Mostly) Know What They Know
- **掲載**: arXiv:2207.05221
- **URL**: https://arxiv.org/abs/2207.05221
- **一言**: Anthropic によるLLMの自己評価能力の最初期の大規模実証研究。"mostly know"がキーフレーズ。
- **本研究との関連**: 本研究の直接の先行研究。方法論のベースライン。

### B-2 ⭐重要
- **著者**: Lin, S., Hilton, J., & Evans, O.
- **年**: 2022
- **タイトル**: Teaching Models to Express Their Uncertainty in Words
- **掲載**: TMLR 2022
- **URL**: https://arxiv.org/abs/2205.14334
- **一言**: 不確かさを言語化させる手法を提案。fine-tuningにより改善可能と示す。
- **本研究との関連**: verbalized uncertainty の概念定義。

### B-3 ⭐重要
- **著者**: Tian, K., Mitchell, E., Zhou, A., et al.
- **年**: 2023
- **タイトル**: Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores
- **掲載**: EMNLP 2023
- **URL**: https://arxiv.org/abs/2305.14975
- **一言**: LLMにただ「確信度を出して」と聞くだけで、内部確率より良い calibration が得られると報告。
- **本研究との関連**: 本研究のプロンプト戦略の根拠。

### B-4 ⭐重要
- **著者**: Xiong, M., Hu, Z., Lu, X., et al.
- **年**: 2024
- **タイトル**: Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs
- **掲載**: ICLR 2024
- **URL**: https://arxiv.org/abs/2306.13063
- **一言**: 複数モデル・複数タスクでの体系的評価。
- **本研究との関連**: 実験デザインの参考。英語中心だった部分を日本語で補完する。

### B-5
- **著者**: Mielke, S. J., Szlam, A., Dinan, E., & Boureau, Y.-L.
- **年**: 2022
- **タイトル**: Reducing Conversational Agents' Overconfidence through Linguistic Calibration
- **掲載**: TACL 2022
- **URL**: https://arxiv.org/abs/2012.14983
- **一言**: 対話エージェントの過信を言語表現で緩和する手法。
- **本研究との関連**: 言語的表現と確信度の関係。

---

## C. LLM評価・ベンチマーク

### C-1
- **著者**: Hendrycks, D., et al.
- **年**: 2021
- **タイトル**: Measuring Massive Multitask Language Understanding
- **掲載**: ICLR 2021
- **URL**: https://arxiv.org/abs/2009.03300
- **一言**: MMLU ベンチマーク。57分野の知識評価。
- **本研究との関連**: 英語での標準的な LLM 評価ベンチマーク。

### C-2
- **著者**: Cobbe, K., et al.
- **年**: 2021
- **タイトル**: Training Verifiers to Solve Math Word Problems
- **掲載**: arXiv:2110.14168
- **URL**: https://arxiv.org/abs/2110.14168
- **一言**: GSM8K データセットの発表論文。
- **本研究との関連**: 数学ドメインの評価手法。

### C-3
- **著者**: Shi, F., et al.
- **年**: 2023
- **タイトル**: Language Models are Multilingual Chain-of-Thought Reasoners (MGSM)
- **掲載**: ICLR 2023
- **URL**: https://arxiv.org/abs/2210.03057
- **一言**: GSM8Kを多言語化（日本語含む）。
- **本研究との関連**: 数学ドメインの日本語評価に使える。

---

## D. 日本語LLM評価

### D-1
- **著者**: llm-jp コミュニティ
- **年**: 2024
- **タイトル**: llm-jp-eval: 日本語大規模言語モデルの評価フレームワーク
- **URL**: https://github.com/llm-jp/llm-jp-eval
- **一言**: 日本語LLM評価の標準ツール。複数タスクを統合。
- **本研究との関連**: 日本語タスクの選定根拠。

### D-2
- **著者**: 藤井, 岡崎 et al.
- **年**: 2024
- **タイトル**: Swallow: 継続事前学習による日本語LLMの構築
- **URL**: https://tokyotech-llm.github.io/swallow
- **一言**: 日本語特化LLMの代表例。
- **本研究との関連**: 評価対象モデル。

### D-3
- **著者**: 栗原 et al.（ELYZA）
- **年**: 2023
- **タイトル**: ELYZA-japanese-Llama 技術報告
- **一言**: 日本語LLMの商用実装。
- **本研究との関連**: 評価対象モデル。

### D-4
- **著者**: Kurihara, K., et al.
- **年**: 2022
- **タイトル**: JGLUE: Japanese General Language Understanding Evaluation
- **掲載**: LREC 2022
- **一言**: 日本語GLUEベンチマーク。
- **本研究との関連**: 常識タスクで JCommonsenseQA を使う根拠。

---

## E. 幻覚（Hallucination）研究

### E-1
- **著者**: Ji, Z., et al.
- **年**: 2023
- **タイトル**: Survey of Hallucination in Natural Language Generation
- **掲載**: ACM Computing Surveys
- **URL**: https://arxiv.org/abs/2202.03629
- **一言**: 幻覚の類型・原因・対策のサーベイ。
- **本研究との関連**: 幻覚と過信の関係を論じる際の基礎文献。

### E-2
- **著者**: Huang, L., et al.
- **年**: 2023
- **タイトル**: A Survey on Hallucination in Large Language Models
- **URL**: https://arxiv.org/abs/2311.05232
- **一言**: LLM時代の幻覚に特化した最新サーベイ。
- **本研究との関連**: 背景知識。

---

## F. 関連する社会・倫理研究

### F-1
- **著者**: Bender, E. M., Gebru, T., McMillan-Major, A., & Shmitchell, S.
- **年**: 2021
- **タイトル**: On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?
- **掲載**: FAccT 2021
- **一言**: LLMの社会的リスクを論じた著名論文。
- **本研究との関連**: 過信がユーザーに与える影響の論拠。

---

## G. 動的認識論理（DEL）— 理論的フレーミング用 ⭐教員専門

> 本カテゴリは 2026-04-09 夜に追加。`research/advisor-theme-alignment.md` で
> 詳述した DEL フレーミングの根拠文献。精読は必須ではなく「第 1, 2 章を
> 斜め読みして公理系と基本演算子を把握する」レベルで十分。

### G-1 ⭐重要
- **著者**: van Ditmarsch, H., van der Hoek, W., & Kooi, B.
- **年**: 2007
- **タイトル**: Dynamic Epistemic Logic
- **掲載**: Synthese Library, Vol. 337, Springer
- **一言**: DEL の標準教科書。第 1, 2 章で K/B 演算子と S5/KD45 公理系を
  解説し、第 4〜5 章で公共発表 `[!φ]` と行動モデル `[A]` を導入する。
- **本研究との関連**: 本研究の DEL フレーミングの理論的基盤。
- **読み方**: 第 1, 2 章を最優先（S5/KD45 の理解）。以降は必要に応じて。

### G-2
- **著者**: Fagin, R., Halpern, J. Y., Moses, Y., & Vardi, M. Y.
- **年**: 1995
- **タイトル**: Reasoning About Knowledge
- **掲載**: MIT Press
- **一言**: 認識論理の古典的教科書。DEL の前身である静的認識論理の
  体系的解説。マルチエージェント知識表現の基礎。
- **本研究との関連**: K 演算子の意味論と公理系を理解するための古典。
- **読み方**: 入手できれば参考文献として引用。精読は任意。

### G-3
- **著者**: 小野, 寛晰
- **年**: 1994
- **タイトル**: 情報科学における論理
- **掲載**: 日本評論社
- **一言**: 日本語で読める様相論理・認識論理の入門書。
- **本研究との関連**: 日本語の用語確定に使える（「様相」「認識論理」等）。
- **読み方**: 大学図書館で取り寄せ。必要箇所のみ斜め読み。

### G-4
- **著者**: Baltag, A., & Renne, B.
- **年**: 2016 (updated)
- **タイトル**: Dynamic Epistemic Logic
- **掲載**: Stanford Encyclopedia of Philosophy
- **URL**: https://plato.stanford.edu/entries/dynamic-epistemic/
- **一言**: 無料で読めるオンライン百科事典項目。van Ditmarsch 教科書の
  要点を簡潔にまとめている。
- **本研究との関連**: まず G-1 に取り組む前に、この項目で全体像を把握する。
- **読み方**: 最初の 30 分で概要を掴むのに最適。

### G-5 ⭐重要（2026-04-10 検索で発見）
- **著者**: （要確認・EMNLP 2025 著者一覧）
- **年**: 2025
- **タイトル**: DEL-ToM: Inference-Time Scaling for Theory-of-Mind Reasoning via Dynamic Epistemic Logic
- **掲載**: EMNLP 2025
- **URL**: https://aclanthology.org/2025.emnlp-main.573/
- **一言**: DEL を使って LLM の Theory-of-Mind 推論を改善。公共発表演算子で
  信念更新をトレースし、inference-time compute で最良のトレースを選択する。
- **本研究との関連**: **直接の比較対象**。ただし DEL-ToM は「DEL で推論を改善する」
  処方的アプローチであり、本研究の「DEL で calibration を解釈する」記述的アプローチ
  とは異なる。第 2 章で明確に差別化する必要あり。
- **読み方**: abstract + introduction + conclusion を精読。方法論の差異を把握する。

### G-6（2026-04-10 検索で発見）
- **著者**: （要確認）
- **年**: 2024
- **タイトル**: Epistemic Integrity in Large Language Models
- **掲載**: arXiv:2411.06528 / OpenReview
- **URL**: https://arxiv.org/abs/2411.06528
- **一言**: LLM の「認識的整合性」—— 表現する確信度と内部状態の一致を研究。
  言語的 assertiveness の測定により、calibration error を 50% 以上削減する手法を報告。
- **本研究との関連**: 認識的整合性の概念は本研究の問題意識と近い。
  ただし DEL の公理系との明示的対応は取っていない。

### G-7（2026-04-10 検索で発見）
- **著者**: （要確認）
- **年**: 2024
- **タイトル**: Do Large Language Models Know What They Don't Know? Evaluating Epistemic Calibration via Prediction Markets
- **掲載**: arXiv:2512.16030
- **URL**: https://arxiv.org/abs/2512.16030
- **一言**: 予測市場メカニズムを使った LLM の認識的キャリブレーション評価。
- **本研究との関連**: 認識的キャリブレーションという概念は近いが、DEL とは独立した
  枠組み。日本語視点もなし。

---

## 読書計画（Week 1〜Week 4）

### Week 1（4月第2週〜第3週）
- [ ] B-1（Kadavath 2022）⭐ 最優先で精読
- [ ] B-3（Tian 2023）⭐ 本研究の方法論の直接参考
- [ ] A-1（Guo 2017）⭐ ECEの定義を理解

### Week 2（4月第4週）
- [ ] B-2（Lin 2022）
- [ ] B-4（Xiong 2024）
- [ ] C-2（GSM8K）

### Week 3（5月第1週）
- [ ] A-2（Desai 2020）
- [ ] C-1（MMLU）
- [ ] C-3（MGSM）
- [ ] D-1（llm-jp-eval）

### Week 4（5月第2週）
- [ ] E-1, E-2（Hallucinationサーベイ）
- [ ] F-1（Stochastic Parrots）
- [ ] 日本語関連論文 D-2〜D-4

### DEL 理論学習（並行・時間があれば）
- [ ] G-4（SEP オンライン項目）— 最初の 30 分
- [ ] G-1（van Ditmarsch et al.）— 第 1, 2 章のみ
- [ ] G-5 検索（既存の DEL × LLM 研究の存在確認）— 30 分

---

## 文献調査のメモ

### 検索キーワード
- **英語**: "LLM calibration", "verbalized confidence", "uncertainty expression", "confidence elicitation", "LLM self-evaluation"
- **日本語**: "大規模言語モデル 信頼度", "LLM 不確実性", "キャリブレーション 日本語"

### 使うデータベース
1. **Google Scholar** ... 主に最新論文とCitationの追跡
2. **Semantic Scholar** ... 関連論文の発見
3. **arXiv** ... プレプリント
4. **ACL Anthology** ... NLP主要会議の論文
5. **CiNii Research** ... 日本語論文
6. **J-STAGE** ... 日本の学会誌

### 被引用数が多い論文から読む
- Kadavath 2022 → 被引用 500+
- Guo 2017 → 被引用 4000+
- これらの「引用元」検索で最新研究をたどる

---

## 次のアクション

- [ ] 上記論文の PDF を Zotero に取り込む
- [ ] 読んだ論文は `templates/literature-card.md` を使って要約
- [ ] 4月末までに Week 1〜2 の論文を精読完了
- [ ] 指導教員に「このリストで方向性が合っているか」を確認
