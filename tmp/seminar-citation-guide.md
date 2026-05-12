# ゼミ発表 参考文献注釈ガイド

> **作成日**: 2026-05-12
> **用途**: ゼミ週次発表スライドに参考文献番号を付けるための対応表

---

## 凡例

- `[n]` = スライドに入れる参考文献番号
- **太字** = 該当箇所の原文（抜粋）
- → = 対応する文献と根拠

---

## 1. 研究テーマ

注釈不要。自分のテーマ定義なので文献参照は不要。

---

## 2. 研究背景

### 2-a. LLM 普及と課題

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| ハルシネーション問題の言及 | **「誤った情報を自信ありげに生成する」いわゆるハルシネーション問題** | [1] Ji et al. (2023) "Survey of Hallucination in NLG", *ACM Computing Surveys* | ハルシネーションの定義・分類の標準的サーベイ |

### 2-b. 問題の本質

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| 正答率と自信度の乖離 | **「実際の正答率」と「モデル自身が表明する自信度」が乖離している** | [2] Guo et al. (2017) "On Calibration of Modern Neural Networks", *ICML 2017* | calibration（乖離）の概念と ECE 指標の出典 |

### 2-c. 先行研究からの着想

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| 内部確率より直接質問が良い | **「内部softmax確率を利用するよりも、モデル自身に"どの程度自信があるか"を直接質問する方が、より良いキャリブレーションが得られる」** | [3] Tian et al. (2023) "Just Ask for Calibration", *EMNLP 2023* | verbalized confidence > 内部確率 を実証した論文。この主張の直接の出典 |
| （補強として） | 同上 | [4] Xiong et al. (2024) "Can LLMs Express Their Uncertainty?", *ICLR 2024* | 複数モデルで同様の結果を確認。[3] の知見の頑健性を示す |

---

## 3. 本研究の位置づけ

### 3-a. 長期的ビジョン・現状の課題

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| ハルシネーション対策は多数研究されているが決定的解決法なし | **「決定的な解決法・汎用的な改善手法はまだ確立されていない」** | [1] Ji et al. (2023) （再掲） | サーベイで対策手法の現状と限界を網羅的に示している |

### 3-b. 本研究の特徴

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| 日本語環境での体系的検証 | **「日本語環境における LLM の自己評価能力を体系的に検証する」** | 注釈不要（自分の研究の新規性の主張） | ただし「英語中心で日本語が空白」の根拠として口頭で補足するなら [3][4] を参照（両論文とも英語タスクのみ） |

---

## 4. リサーチクエスチョン

### メイン RQ

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| 確信度と正答率の整合性 | **「確信度は実際の正答率とどの程度整合しているか」** | 注釈不要（自分の RQ） | ただし RQ の着想元として口頭で言及するなら [5] Kadavath et al. (2022) を挙げる |

### サブ RQ

注釈不要。RQ 自体は自分の設定なので文献参照は不要。
質疑で「なぜこの条件を選んだか」と聞かれた場合の備え：

| サブ RQ | 質疑対応用の文献 |
|---|---|
| ① モデル間比較 | [4] Xiong et al. (2024) がモデル間比較を実施（英語） |
| ② ドメイン比較 | [5] Kadavath et al. (2022) がドメイン別分析を実施 |
| ③ 確信度表現比較 | [3] Tian et al. (2023) が複数プロンプト方式を比較 |
| ④ 言語比較 | 先行研究なし（本研究の新規性） |

---

## 5. 研究手法

### 5-a. 基本方針

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| 複数モデル・複数タスク・複数プロンプト条件 | **「複数モデル・複数タスク・複数プロンプト条件で実験」** | [4] Xiong et al. (2024) | 同様の多条件実験設計の先行例 |

### 5-b. 正答判定方法

| 箇所 | 原文（抜粋） | 文献 | 理由 |
|---|---|---|---|
| LLM-as-a-Judge | **「別の LLM に5段階評価を行わせる LLM-as-a-Judge 的な評価方法」** | [6] Zheng et al. (2023) "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", *NeurIPS 2023* | LLM-as-a-Judge の概念の出典。**現在の文献リストに未掲載なので追加が必要** |

---

## 参考文献リスト（スライド末尾用）

```
[1] Ji, Z., et al. (2023). Survey of Hallucination in Natural Language
    Generation. ACM Computing Surveys, 55(12), 1-38.

[2] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On
    Calibration of Modern Neural Networks. Proc. ICML 2017.

[3] Tian, K., Mitchell, E., Zhou, A., et al. (2023). Just Ask for
    Calibration: Strategies for Eliciting Calibrated Confidence Scores
    from Language Models Fine-Tuned with Human Feedback. Proc. EMNLP 2023.

[4] Xiong, M., Hu, Z., Lu, X., et al. (2024). Can LLMs Express Their
    Uncertainty? An Empirical Evaluation of Confidence Elicitation in
    LLMs. Proc. ICLR 2024.

[5] Kadavath, S., Conerly, T., Askell, A., et al. (2022). Language
    Models (Mostly) Know What They Know. arXiv:2207.05221.

[6] Zheng, L., et al. (2023). Judging LLM-as-a-Judge with MT-Bench
    and Chatbot Arena. Proc. NeurIPS 2023.
    ※ 文献リスト未掲載 → 追加推奨
```

---

## 注意事項

1. **[5] Kadavath 2022 は arXiv プレプリント**（未査読）。ゼミ発表では問題ないが、卒論本文では「査読済み論文が引用する重要プレプリント」として扱う
2. **[6] Zheng 2023 は現在の文献リストに未掲載**。LLM-as-a-Judge に言及するなら追加が必要
3. スライド中の注釈は `[1]` 等の番号で十分。フルの書誌情報は最終スライドにまとめる
4. 「キャリブレーションとは」の説明パートは自分の言葉での解説なので注釈不要。ただし ECE の正式な定義として [2] を挙げてもよい
