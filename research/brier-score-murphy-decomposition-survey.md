# Brier Score と Murphy 分解：分野横断調査レポート

> **作成日**: 2026-06-24
> **目的**: Brier Score の多分野での使われ方と Murphy 分解の弱点・発展形を調査し、本研究への適用可能性を判断する

---

## 1. Brier Score の起源と定義

**提案者**: Glenn W. Brier（米国気象学者）、**1950年**

```
BS = (1/N) × Σ (pᵢ − yᵢ)²
```

- pᵢ: モデルの確信度（0.0〜1.0）
- yᵢ: 正誤ラベル（正解=1, 不正解=0）
- 値域: 0.0〜1.0、低いほど良い
- **Proper Scoring Rule**: 真の確率を正直に報告することが最良スコアになる

---

## 2. 分野別の使われ方

### 2.1 気象予測（発祥の地）

**最も成熟した使用例。**

- ECMWF（欧州中期予報センター）が日常業務で使用
- 「雨が降るか否か」「台風が上陸するか否か」などの二値確率予報の評価
- **Brier Skill Score（BSS）**に発展：`BSS = 1 − BS / BS_clim`
  - 気候値（climatology）をベースラインとして相対化
  - BSS > 0 = 気候値より良い予測、BSS = 1 = 完璧
  - **LLM 研究では "Brier Skill Score" という視点がほぼ存在しない**

### 2.2 医療・臨床予測

**生存分析での応用が特に発展している。**

- がん予後予測、心疾患リスク評価、疾患進行モデルなどで標準的に使用
- **Integrated Brier Score（IBS）**：生存分析用の拡張版
  - 観察打ち切り（censoring）に対応するため逆確率重み付き（IPCW）を使用
  - 時刻 t での生存確率 S(t|x) の二乗誤差を時間軸で積分
  - C-index（AUROC の生存版）との組み合わせがゴールドスタンダード
  - `scikit-survival` ライブラリに実装済み
- 医療意思決定における較正（calibration）評価に不可欠

### 2.3 金融・信用リスク

- クレジットデフォルト予測（PD: Probability of Default）の評価に使用
- AUC（ROC曲線下面積）だけでは較正精度を評価できないため Brier Score が補完
- 「確信度の質」が金融モデルでも重要になってきている

### 2.4 予測トーナメント・予測市場

**人間の予測能力の評価指標として確立。**

- Philip Tetlock の研究（Good Judgment Project）でスーパーフォーキャスターの評価に使用
- Metaculus、Good Judgment Open 等のプラットフォームでの個人スコアに使用
- **LLM vs 人間の比較基準として近年急速に注目**：
  - スーパーフォーキャスター: BS ≈ 0.074〜0.122
  - Metaculus 一般ユーザー: BS ≈ 0.149
  - o3（LLM）: BS ≈ 0.135 → 一般ユーザーより良いがスーパーフォーキャスターには及ばず
  - **→ LLM のキャリブレーション研究と予測市場の文脈が接続されつつある**

### 2.5 機械学習・NLP・LLM（最新動向）

- ECE・AUROC とセットで報告するのが標準化されつつある
- Tian 2023・Xiong 2024 等の calibration 論文では副指標として使用
- **verbalized confidence の評価に Brier Score を使った論文は増加中**（2024〜2025）
- ただし Murphy 分解を適用した LLM 論文は**現時点で確認できない**

---

## 3. Brier Score の主要変種

| 変種 | 説明 | 使用分野 |
|---|---|---|
| Brier Score（BS） | 基本形 | 全分野 |
| Brier Skill Score（BSS） | 気候値ベースラインに対して相対化 | 気象・予測市場 |
| Integrated Brier Score（IBS） | 打ち切りデータに対応、時間軸で積分 | 医療・生存分析 |
| Weighted Brier Score | クラス不均衡・トピック多様性に対応 | 予測トーナメント・医療 |
| Time-dependent BS | 各時刻での BS を計算 | 生存分析 |

---

## 4. Murphy 分解の詳細

### 4.1 基本形

```
BS = REL − RES + UNC

REL（Reliability）  = Σₖ (nₖ/n) × (f̄ₖ − ōₖ)²    ← 低いほど良
RES（Resolution）   = Σₖ (nₖ/n) × (ōₖ − ō)²       ← 高いほど良
UNC（Uncertainty）  = ō × (1 − ō)                   ← データ固有の定数
```

- f̄ₖ: グループ k の平均確信度
- ōₖ: グループ k の正答率
- ō: 全体の正答率
- n: 総サンプル数、nₖ: グループ k のサンプル数

### 4.2 各成分の直感的意味

| 成分 | 問い | 値の解釈 |
|---|---|---|
| REL | 「70% 確信のとき本当に 70% 正解か？」 | 0 = 完璧な較正 |
| RES | 「正解と不正解で確信度が異なるか？」 | 大きいほど識別力高い |
| UNC | 「そもそもこの問題は難しいか？」 | データ固有、制御不能 |

### 4.3 Murphy 分解の既知の弱点

| 弱点 | 詳細 |
|---|---|
| **ビン依存性** | グループ化（ビニング）が必要。ビン数・境界の取り方で値が変わる |
| **REL と ECE の重複** | どちらも「確信度と正答率のズレ」を測る。情報が被る |
| **RES の解釈問題** | AUROC より直感的でない。"ランキング正確度" とは微妙に違う |
| **UNC が定数** | データを固定すれば UNC は変わらない。比較に使えない |
| **推定誤差** | サンプルが少ないと REL・RES の推定が不安定になる（Ferro & Fricker 2012） |
| **成分間の依存性** | BS = REL − RES + UNC なので 3 成分のうち 2 つを知れば残り 1 つは自動的に決まる（自由度 2）|

### 4.4 気象分野での発展と改善

#### Bröcker (2009)「Reliability, Sufficiency, and the Decomposition of Proper Scores」
**最重要論文。** Murphy 分解を Brier Score 専用から**任意の Proper Scoring Rule（PSR）に一般化**。

> 「任意の PSR に対して REL−RES+UNC 分解が成立する」

- Log-loss、CRPS、Quantile Score にも Murphy 分解が適用できることを証明
- ビン依存性の問題は残るが、指標の選択自由度が広がった
- arXiv:0806.0813

#### Siegert (2017)「Simplifying and generalising Murphy's Brier score decomposition」
- 元の Murphy 分解の導出を簡潔化
- 一般的な条件への拡張方法を整理
- QJRMS 143(703), 1178–1187

#### Ferro & Fricker (2012)「Variance estimation for Brier Score decomposition」
- Murphy 分解の推定誤差（分散）の計算方法を確立
- 「統計的に有意な差があるか」を検定できるようになった
- arXiv:1303.6182

#### Pohle (2020)「The Murphy Decomposition and the Calibration-Resolution Principle」
- REL（較正）と RES（解像度）を「較正-解像度の原則」として統一理論化
- arXiv:2005.01835

#### Allen et al. (2023)「A conditional decomposition of proper scores」
- 条件付き分解として拡張
- QJRMS 149, 4478

#### 「Two Extra Components」(2008, Monthly Weather Review)
- ビニング誤差による付加成分（within-bin variance・covariance）を発見
- ビン数が少ないと REL + RES + UNC ≠ BS になる現象を説明

### 4.5 CRPS（Continuous Ranked Probability Score）との関係

- CRPS = Brier Score の連続値版（回帰の確率予測を評価）
- CRPS にも Murphy 分解が適用可能（Hersbach 2000; arXiv:2311.14122）
- LLM の verbalized confidence は 0.0〜1.0 の離散値なので CRPS より BS が適切

---

## 5. LLM 研究への適用可能性

### 5.1 現状のギャップ

| 指標 | LLM 研究での使用状況 |
|---|---|
| ECE | 主要指標として広く使用 |
| Brier Score | 補助指標として使用（単一数値のみ） |
| AUROC | 補助指標として使用 |
| **Murphy 分解** | **現時点で LLM 論文での使用例なし** |
| Brier Skill Score | LLM 論文では使用例なし |

### 5.2 Murphy 分解を使う場合の想定結果

プロンプト条件ごとに REL と RES が**独立に動く**可能性がある：

| 条件 | 予測される変化 | 解釈 |
|---|---|---|
| Verb.1S | REL 改善、RES やや改善 | 同時出力がスケールと識別力を両方調整 |
| Verb.2S | RES が顕著に改善 | 2段階の再考プロセスが識別力を向上させる |
| Ling.1S | REL は変化少、RES 改善 | 言語表現は順序は正しいが絶対値調整は弱い |

→ この予測が実験で確認できれば「なぜ Verb.2S が有効か」の機序を初めて定量的に示せる。

### 5.3 Brier Skill Score の活用可能性

気象分野で定着している BSS を LLM に適用する先行研究もほぼない。

```
BSS = 1 − BS / BS_ref

BS_ref = ō × (1 − ō)  = UNC（ランダム予測のベースライン）
```

BSS = 0 = ランダム予測と同等、BSS = 1 = 完璧、BSS < 0 = ランダムより悪い

→ 「このプロンプト方式はランダムより何%良いか」という直感的な指標になる。

---

## 6. 本研究への推奨

### 採用確定（ベースライン）
- ECE、Brier Score（単一値）、AUROC

### 探索的追加（実験後に判断）
- **Murphy 分解**（REL / RES 分離）：プロンプト条件間で REL と RES の順位が逆転するケースがあれば採用
- **Brier Skill Score（BSS）**：追加コストほぼゼロ。ランダムベースラインとの比較として補助的に添付するだけで価値あり

### 見送り
- IBS（生存分析用、本研究には不要）
- CRPS（連続値予測用、本研究の離散 0/1 判定には不要）

---

## 7. 参考文献

- Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review*, 78(1), 1–3.
- Murphy, A. H. (1973). A new vector partition of the probability score. *Journal of Applied Meteorology*, 12(4), 595–600.
- Bröcker, J. (2009). Reliability, sufficiency, and the decomposition of proper scores. *QJRMS*, 135(643), 1512–1519. [arXiv:0806.0813](https://arxiv.org/abs/0806.0813)
- Ferro, C. A. T. & Fricker, T. E. (2012). Variance estimation for Brier score decomposition. [arXiv:1303.6182](https://arxiv.org/pdf/1303.6182)
- Siegert, S. (2017). Simplifying and generalising Murphy's Brier score decomposition. *QJRMS*, 143(703), 1178–1187.
- Pohle, M.-O. (2020). The Murphy decomposition and the calibration-resolution principle. [arXiv:2005.01835](https://arxiv.org/abs/2005.01835)
- Allen, S. et al. (2023). A conditional decomposition of proper scores. *QJRMS*, 149, 4478. 
- Hersbach, H. (2000). Decomposition of the CRPS for ensemble prediction systems. *Weather and Forecasting*, 15(5), 559–570.
