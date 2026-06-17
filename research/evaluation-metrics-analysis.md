# 評価指標の選定分析

> **作成日**: 2026-06-17
> **目的**: 本研究における評価指標の選定根拠を文書化する
> **ステータス**: 調査完了・指標確定（次回ゼミで報告予定）

---

## 1. 候補指標の全体マップ

LLM の verbalized confidence を対象としたキャリブレーション研究で利用可能な指標は以下に整理できる。

| カテゴリ | 指標名 | 略称 |
|---|---|---|
| **キャリブレーション（ビニング系）** | Expected Calibration Error | ECE |
| | Maximum Calibration Error | MCE |
| | Adaptive Calibration Error | ACE |
| | Static Calibration Error | SCE |
| | Classwise ECE | cw-ECE |
| **キャリブレーション（スコアリングルール系）** | Brier Score | BS |
| | 対数損失 / 負の対数尤度 | Log-loss / NLL |
| **識別能力（Discrimination）** | Area Under ROC Curve | AUROC |
| | Area Under Precision-Recall Curve | AUPRC |
| | Area Under Risk-Coverage Curve | AUARC |
| **可視化** | Reliability Diagram | — |
| **尖鋭度** | Sharpness | — |

---

## 2. 各指標の詳細

### 2-1. ECE（Expected Calibration Error）

**定義（数式）**

予測確信度を M 個の等幅ビン（通常 M=10）に分割し、各ビン内の「平均確信度」と「平均正答率」の差の重み付き平均を取る。

```
ECE = Σ_{m=1}^{M} (|B_m| / n) × |acc(B_m) - conf(B_m)|
```

- `B_m`: ビン m に属するサンプル集合
- `n`: 総サンプル数
- `acc(B_m)`: ビン m 内の正答率
- `conf(B_m)`: ビン m 内の平均確信度

完全キャリブレーション = ECE = 0（低いほど良い）

**出典**: Guo et al. (2017, ICML) が深層学習に適用して普及。原概念は Naeini et al. (2015)。

**長所**
- 解釈が直感的（「確信度と正答率のズレ」そのもの）
- 先行研究（Tian 2023, Xiong 2024 等）との比較可能性が高い
- 標準的な指標として研究コミュニティで広く採用されている

**短所**
- **真の意味での Proper Scoring Rule ではない**（後述）。理論的には、均一な予測や定数予測でも ECE = 0 になりうる
- **ビン数・ビン分割方法に依存する**（M=10 と M=15 で結果が変わりうる）
- LLM の予測は高確信度域に集中しやすく、等幅ビンでは低確信度ビンが空になりやすい（Nixon et al. 2019）
- ECE の推定値には統計的バイアスがある（有限サンプルでは過小評価）

---

### 2-2. MCE（Maximum Calibration Error）

**定義（数式）**

ビニングは ECE と同様だが、重み付き平均ではなく「最大値」を取る。

```
MCE = max_{m=1,...,M} |acc(B_m) - conf(B_m)|
```

完全キャリブレーション = MCE = 0

**長所**
- 最悪ケースのミスキャリブレーションを捉える
- 高リスク・安全性重視のドメイン（医療診断、自動運転等）に適合

**短所**
- 一つのビンの外れ値に過敏
- 「全体的にどの程度ズレているか」を反映しない
- LLM のキャリブレーション研究ではあまり使われない

**本研究との関連**: メインRQが「全体的な整合性」を問うため、MCE は主指標には不適。補助的参考値として報告は可能。

---

### 2-3. ACE（Adaptive Calibration Error）

**定義**

ECE の「等幅ビン」を「等質量ビン（各ビン内のサンプル数が等しくなるよう境界を調整）」に変えた指標。Nixon et al. (2019, CVPR Workshop) が提案。

```
ACE = Σ_{m=1}^{M} (1/M) × |acc(B_m) - conf(B_m)|
```

（等質量ビンなら |B_m|/n ≈ 1/M になる）

**長所**
- LLM のように高確信度に予測が偏る場合、等幅ビンよりも偏りなく評価できる
- ビン分割の任意性を低減できる
- Nixon et al. (2019) の実験では ECE より安定したランキングを提供

**短所**
- 等幅ビンとの直接比較ができなくなる（先行研究の数値と比較しにくい）
- 実装によっては結果が変わる

**本研究との関連**: LLM は過信傾向があり高確信度域に予測が集中するため、ACE の方が理論的には望ましい。ただし Tian 2023 との比較可能性のため、ECE（等幅）を主とし ACE を補助として並記する選択肢がある。

---

### 2-4. SCE（Static Calibration Error）・Classwise ECE

**定義**

各クラス k に対して個別に ECE を計算し、クラス間で平均を取る指標。Nixon et al. (2019) は SCE（等幅ビン）、ACE のクラス別拡張版も定義した。

```
SCE = (1/K) × Σ_{k=1}^{K} Σ_{b=1}^{B} (n_{b,k}/N) × |acc(b,k) - conf(b,k)|
```

**本研究との関連**: 本研究の問題設定は「回答が正しいか否か」の二値判定が基本であり、厳密な意味での多クラス分類ではない。ECE（top-label）で十分カバーでき、SCE の追加価値は限定的。省略可。

---

### 2-5. Brier Score（BS）

**定義（数式）**

予測確信度 p_i と正誤ラベル y_i ∈ {0,1} の二乗誤差の平均。

```
BS = (1/N) × Σ_{i=1}^{N} (p_i - y_i)^2
```

完全予測 = BS = 0、ランダム予測 = BS ≈ 0.25（0.5 × 0.5）

**Murphy (1973) 分解**

BS の最も重要な性質：3成分に加法的に分解される。

```
BS = REL - RES + UNC
```

| 成分 | 意味 | 良い方向 |
|---|---|---|
| **REL（Reliability）** | キャリブレーション誤差（確信度 vs 正答率のズレ） | 小さいほど良い |
| **RES（Resolution）** | 識別能力（正解・不正解を区別する能力） | 大きいほど良い |
| **UNC（Uncertainty）** | データ固有の不確実性（制御不能） | 固定値 |

つまり：**Brier Score = （キャリブレーション誤差）−（識別能力）+（固定値）**

**Proper Scoring Rule としての性質**

Brier Score は**厳密に真の意味での Proper Scoring Rule**である（Gneiting & Raftery 2007）。これは：
- 期待 BS を最小化する唯一の最適予測は「真の条件付き確率」そのもの
- 虚偽の確信度を報告しても BS は改善しない
- ECE と異なり、定数予測でも BS = 0 にはなれない

**長所**
- ビニング不要 → ビン数依存の恣意性がない
- Proper Scoring Rule → 理論的保証が強い
- 分解によりキャリブレーション（REL）と識別能力（RES）を分離できる
- 2025年のLLM calibration 研究で急速に採用が増加（ConfTuner NeurIPS2025, RLCR 2025等）

**短所**
- 単一スコアとして見ると「キャリブレーション」と「識別能力」が混在する
- ECE よりも解釈が直感的でない（「何%ズレているか」が明示されない）
- Tian 2023・Xiong 2024 では使われていないため、直接比較に注意が必要

---

### 2-6. Log-loss / NLL（負の対数尤度）

**定義（数式）**

```
LogLoss = -(1/N) × Σ_{i=1}^{N} [y_i × log(p_i) + (1-y_i) × log(1-p_i)]
```

**長所**: 厳密な Proper Scoring Rule、確信度が低い場合に敏感

**短所**: 確信度が 0 や 1 に近い場合に値が発散する（数値的に不安定）、外れ値に過敏

**本研究との関連**: Brier Score と同様に Proper Scoring Rule だが、Brier Score より解釈しにくく、発散リスクもある。Brier Score を採用するなら Log-loss の追加は優先度が低い。

---

### 2-7. AUROC（Area Under ROC Curve）

**定義（概念）**

ランダムに選んだ「正解サンプル」と「不正解サンプル」のペアに対して、モデルが正解サンプルに高い確信度を与える確率。

- AUROC = 0.5: ランダムと同等（確信度が意味を持たない）
- AUROC = 1.0: 完全に正解と不正解を識別できる

**キャリブレーション vs 識別能力（重要な概念的区別）**

| | ECE / Brier Score | AUROC |
|---|---|---|
| **測定対象** | キャリブレーション（確信度の数値的精度） | 識別能力（正解・不正解のランキング能力） |
| **問う内容** | 「70%確信は本当に70%正解か？」 | 「高確信のものが低確信より正しいか？」 |
| **スケール感度** | あり（絶対値が重要） | なし（単調変換に不変）|

**両者は独立した性質**であり、実験的に ECE と AUROC の相関はほぼゼロと報告されている（Revisiting Uncertainty 2025）。

**LLM 研究での使用例**
- Xiong et al. 2024: ECE（キャリブレーション）と AUROC（失敗予測）の両方を報告
- Kuhn et al. 2023「Semantic Entropy」: AUROC 主体
- Mind the Gap (EACL 2026): ECE + AUROC + Brier Score の 3 指標セットを推奨

**長所**: スケール不変（verbalized confidence の絶対値が不安定でも有効）、失敗予測（selective prediction）のベンチマークとして確立している

**短所**: キャリブレーションを直接測定しない。「確信度の数値が意味を持つか」という本研究の核心的問いに直接答えない

---

### 2-8. AUPRC / AUARC

- **AUPRC**: 正解・不正解クラスのサンプル数が大きく偏る場合に AUROC より安定。本研究では精度（正答率）が 50-80% 程度と想定され、著しい不均衡は生じにくいため AUROC で代替可能。
- **AUARC（Area Under Accuracy-Rejection Curve）**: 信頼度の低い予測から順に棄却した際の精度向上を測る。selective prediction の実用性評価に適する。本研究では実験上の棄却操作を行わないため優先度は低い。

---

### 2-9. Reliability Diagram（信頼性図）

数値指標ではなく可視化手段。横軸に確信度、縦軸に実際の正答率をビン毎にプロットし、対角線（完全キャリブレーション）からのズレを視覚化する。

ECE や Brier Score の数値結果を補完するものとして論文の Figure に必ず含めるべき。単体では指標ではない。

---

## 3. 先行研究における指標使用実績

| 論文 | 主指標 | 補助指標 |
|---|---|---|
| Guo et al. 2017 (ICML) | ECE | MCE, Reliability Diagram |
| Kadavath et al. 2022 (arXiv) | ECE, RMS-CE | AUROC |
| Tian et al. 2023 (EMNLP) ★主要参考 | **ECE** | — |
| Xiong et al. 2024 (ICLR) | **ECE** | **AUROC** |
| Kuhn et al. 2023 (ACL) | AUROC | — |
| ConfTuner 2025 (NeurIPS) | ECE | AUROC, Brier Score |
| Mind the Gap 2026 (EACL) | ECE + AUROC + Brier | — |
| RLCR 2025 | Brier Score (reward) | ECE |

---

## 4. 指標比較マトリクス

| 観点 | ECE | ACE | Brier Score | AUROC | MCE |
|---|:---:|:---:|:---:|:---:|:---:|
| キャリブレーション測定 | ✅ | ✅ | ✅（REL成分） | ❌ | ✅（最悪ケース） |
| Proper Scoring Rule | ❌ | ❌ | ✅ | N/A | ❌ |
| ビニング不要 | ❌ | ❌ | ✅ | ✅ | ❌ |
| 先行研究との比較可能性 | ✅✅ | △ | △ | ✅ | △ |
| 直感的解釈しやすさ | ✅ | ✅ | △ | ✅ | ✅ |
| LLM 過信傾向への適合 | △（等幅が弱い） | ✅ | ✅ | ✅ | △ |
| 識別能力の同時測定 | ❌ | ❌ | ✅（RES成分） | ✅ | ❌ |
| 実装の容易さ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 5. 本研究への適用 —— 結論と指標選定

### 5-1. 選定方針

本研究のメインRQは以下の 2 層からなる：

1. **測定層**:「確信度と正答率はどの程度整合しているか」→ キャリブレーション指標が必要
2. **比較層**:「プロンプト方式・モデル・タスク・言語間でどのような差があるか」→ 条件間の比較可能な指標が必要

加えて、本研究は卒論水準（データ量は 4モデル × 4ドメイン × 3プロンプト × 25問 = 1,200 問前後）であり、過度に複雑な指標体系は避けた方がよい。

### 5-2. 選定結果（確定）

```
主指標 : ECE（等幅10ビン）
副指標 : Brier Score
補助指標: AUROC（v0.3 計画書の「supplementary」ポジションで維持）
可視化  : Reliability Diagram（ECE と組み合わせて論文図に掲載）
```

### 5-3. 各指標の採用理由と根拠

#### ✅ ECE を主指標とする理由

1. **先行研究との比較可能性**: 最重要先行研究 Tian 2023（EMNLP）・Xiong 2024（ICLR）がともに ECE を主指標として使用。本研究の核心的主張「日本語環境での再検証」は Tian 2023 の結果（ECE 約50%削減）を基準にする必要があり、ECE が不可欠。
2. **研究RQとの直接的な対応**: 「確信度と正答率の整合性」という問いに ECE は文字通り答える指標。
3. **解釈しやすさ**: ECE = 0.10 であれば「確信度が正答率から平均 10% ズレている」と直感的に説明できる。これは発表・論文の読者への説明において重要。
4. **標準性**: キャリブレーション研究において ECE は事実上の標準指標であり、他の多くの文献との対比が容易。

#### ✅ Brier Score を副指標とする理由

1. **ECE の欠点を補完する**: ECE は Proper Scoring Rule ではなく、理論的な保証が弱い。Brier Score は厳密な Proper Scoring Rule であり、ECE の弱点を補う。
2. **ビニング依存を回避**: ECE のビン数問題（M=10 vs M=15 で結果が変わる問題）に依存しない独立した測定が得られる。
3. **分解による深掘り**: Murphy 分解（BS = REL - RES + UNC）により、キャリブレーション誤差（REL）と識別能力（RES）を分離した分析が可能。これによりモデルの「数値的精度」と「ランキング能力」の違いが明らかになる。
4. **最新潮流への対応**: 2024〜2025 年のLLM キャリブレーション研究（ConfTuner, RLCR, DINCO 等）で Brier Score の採用が急増しており、その理論的優位性が認識されている。

#### ✅ AUROC を補助指標として維持する理由

1. **Xiong 2024 との比較可能性**: Xiong 2024 では AUROC を ECE と並ぶ主要指標として使用している。v0.3 計画書でも「supplementary」として位置づけていた。
2. **キャリブレーションと識別能力の直交性の確認**: ECE と AUROC の相関が低いことが先行研究で示されており、本研究でもその関係を確認することに意義がある。
3. **失敗予測の観点**: 「確信度の低いものを棄却すれば正答率が上がるか」という実用的問いに AUROC が答える。
4. **補助的位置づけが適切**: AUROC はキャリブレーションを直接測定しないため、主指標にするとRQとのズレが生じる。補助指標として適切。

#### ❌ 採用しない指標と理由

| 指標 | 不採用理由 |
|---|---|
| MCE | 最悪ケースの評価。本研究の RQ（全体的整合性）に対応しない |
| ACE（主指標として） | ECE との比較可能性が失われる。補足として提示は可能だが主指標には不適 |
| SCE / cw-ECE | 多クラス設定向け。本研究は二値（正解・不正解）判定が基本 |
| Log-loss / NLL | Brier Score と同様の Proper Scoring Rule だが数値的不安定性（発散リスク）があり Brier Score で代替可 |
| AUPRC | サンプル不均衡が生じにくい本研究では AUROC で代替可 |
| AUARC | 棄却実験を行わない本研究では使用機会がない |

### 5-4. 実装上の注意事項

**ECE の実装パラメータ**
- ビン数: M = 10（先行研究と統一。Tian 2023 に合わせる）
- ビン幅: 等幅（0〜1 を 0.1 刻みで分割）
- 空ビンの扱い: 重み付き平均のため自動的に除外される
- LLM の数値出力（「75%」「0.8」等）は前処理でスケール統一が必要

**Brier Score の実装**
- 二値正誤（y=1 正解, y=0 不正解）に対する平均二乗誤差
- 確信度 p は [0, 1] に正規化
- Murphy 分解のためには確信度値のビニングが必要（実装ライブラリ例: `netcal`, `sklearn.calibration`）

**Reliability Diagram**
- 横軸: 確信度（0〜1 を 10 ビン）
- 縦軸: 実際の正答率
- 対角線（y=x）が完全キャリブレーション
- プロンプト方式×モデル×タスク の組み合わせで複数の Diagram を生成

---

## 6. まとめ表（v0.3 計画書の更新内容）

| 区分 | 指標 | 根拠文献 |
|---|---|---|
| **主指標** | ECE（Expected Calibration Error） | Guo 2017 [2], Tian 2023 [3], Xiong 2024 [4] |
| **副指標** | Brier Score（+ Murphy 分解） | Murphy 1973, Nixon 2019, ConfTuner 2025 |
| **補助指標** | AUROC | Xiong 2024 [4], Kuhn 2023 |
| **可視化** | Reliability Diagram | Guo 2017 [2] |

---

## 参照文献（本文書内で言及）

- Guo, C. et al. (2017). On Calibration of Modern Neural Networks. *ICML 2017*.
- Murphy, A. H. (1973). A New Vector Partition of the Probability Score. *J. Applied Meteorology*.
- Nixon, J. et al. (2019). Measuring Calibration in Deep Learning. *CVPR Workshop 2019*.
- Gneiting, T. & Raftery, A. E. (2007). Strictly Proper Scoring Rules. *JASA 102*(477).
- Tian, K. et al. (2023). Just Ask for Calibration. *EMNLP 2023*.
- Xiong, M. et al. (2024). Can LLMs Express Their Uncertainty? *ICLR 2024*.
- Kuhn, L. et al. (2023). Semantic Uncertainty. *ACL 2023*.
