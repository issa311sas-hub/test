# 文献要約カード: Guo et al. (2017)

> **注意**: このカードは「こういう感じで埋める」という例示のための初期版。
> 実際に精読した後、各セクションを本人の言葉で書き直すこと。

---

## 基本情報

| 項目 | 内容 |
|---|---|
| **著者** | Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger |
| **発行年** | 2017 |
| **タイトル（日本語）** | 現代ニューラルネットワークのキャリブレーションについて |
| **タイトル（原題）** | On Calibration of Modern Neural Networks |
| **掲載誌/学会** | Proceedings of the 34th International Conference on Machine Learning (ICML'17) |
| **DOI / URL** | https://arxiv.org/abs/1706.04599 |
| **BibTeX キー** | `guo2017calibration` |
| **読んだ日** | 2026-04-XX（予定） |
| **重要度** | ★★★（本研究の calibration 指標の出典） |

---

## 内容要約

### 研究目的・問い（RQ）
現代の深層ニューラルネットワーク（特に深く広い ResNet など）は、従来の浅いモデルに
比べて **分類精度は高いが calibration は悪化している** のではないか？
またその改善手法として何が有効か？

### 研究方法
- **対象**: CIFAR-10/100, SVHN, ImageNet などの画像分類、Reuters/20News のテキスト分類
- **モデル**: LeNet, ResNet, DenseNet, Wide ResNet など多様なアーキテクチャ
- **手法**:
  - Reliability Diagram による視覚的分析
  - **Expected Calibration Error (ECE)** の提案・普及
  - Temperature Scaling を含む複数の post-hoc calibration 手法を比較
- **分析**:
  - 深さ・幅・正則化が calibration に与える影響を ablation 的に検証
  - 複数手法（Platt, Histogram Binning, Isotonic Regression, Matrix/Vector Scaling, Temperature Scaling）のベンチマーク

### 主な結果
1. 現代の深層モデルは LeNet5 のような古いモデルと比べて **ECE が 10 倍程度悪化** している
2. **Temperature Scaling**（単一のスカラ T で logits を割るだけ）が最も単純で効果的な手法
3. weight decay の強化は accuracy に影響せず calibration を改善する
4. Batch Normalization や深さの増加は calibration を悪化させる傾向がある

### 結論・主張
深いニューラルネットワークは過信傾向があるが、Temperature Scaling のような軽量な
post-hoc 手法で簡単に改善できる。calibration は精度とは別の独立した評価軸である。

### 研究の限界
- 対象が画像分類（＋少量のテキスト分類）に限定
- softmax 確率に対する calibration のみを扱っており、生成モデルや言語化された
  確信度（verbalized confidence）には触れていない
- 訓練時の calibration（学習アルゴリズムの改良）は対象外

---

## 自分の研究との関連

### この研究が自分の卒論に役立つ点
- **ECE の定義の原典**として、第3章 3.5.1 で必ず引用する
- Reliability Diagram の説明・図解も本論文のスタイルを踏襲できる
- 「精度と calibration は独立」という主張は、本研究の第4章で「Swallow は精度は
  低いが calibration も悪い」といった結果を解釈する際の根拠となる
- Temperature Scaling の説明を 2.1.3 の「calibration 改善手法」で簡潔に紹介

### 自分の研究との違い・差別化ポイント
| 観点 | Guo et al. (2017) | 本研究 |
|---|---|---|
| 対象タスク | 画像分類中心 | 日本語自然言語 QA |
| 対象モデル | CNN系 | LLM（Transformer系） |
| 確信度の種類 | softmax 確率 | verbalized（言語化された数値） |
| 言語 | 英語（タスクに依存） | 日本語中心・一部英語 |
| 評価指標 | ECE 中心 | ECE, Brier, AUROC の併用 |

**差別化の主張**: Guo らは softmax 確率の calibration を論じたが、LLM の時代には
モデルが自然言語で「XX%自信がある」と答えるようになった。この言語化された確信度は
softmax とは質的に異なるため、別途の検証が必要である。

### 引用予定の章
- 第1章 序論（calibration 問題の一般的な説明）
- 第2章 関連研究 2.1.1（calibration 問題の発見）、2.1.3（改善手法）
- 第3章 研究方法 3.5.1（ECE の定義式）

---

## メモ・気になったこと

- ECE の計算ビン数は論文では 15 を推奨しているが、本研究では先行研究に倣い 10 を採用予定
- Temperature Scaling は LLM の verbalized confidence には直接適用できないため、
  本研究では触れるが深追いしない
- 「accuracy は保ったまま calibration だけ改善」という本論文の枠組みは、本研究の
  考察（第5章）で「精度指標と calibration 指標を切り離して評価する必要性」を主張する
  根拠として使える

---

## 直接引用候補

```
[精読後に埋める]
- p. XX: 「Modern neural networks are no longer well-calibrated...」
- p. XX: ECE の定義式（式番号を記録）
- p. XX: Temperature Scaling の定義
```

---

## 関連論文（要チェック）

- Platt (1999): Probabilistic outputs for SVMs（Platt Scaling の原典）
- Zadrozny & Elkan (2002): Isotonic regression for probability estimation
- Niculescu-Mizil & Caruana (2005): Obtaining calibrated probabilities
- Naeini et al. (2015): Bayesian Binning（ECE の改良版 BBE の提案）
