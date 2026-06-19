# 実験環境構築ガイド

> **作成日**: 2026-06-19
> **対象研究**: プロンプト設計による LLM キャリブレーション性能向上
> **調査対象論文**: Tian 2023 / Xiong 2024 / Yang 2024 / Xue 2025

---

## 1. 各論文の GitHub リポジトリ

| 論文 | リポジトリ |
|---|---|
| Tian et al. 2023 (EMNLP) | https://github.com/kanishkg/boxing-gym |
| Xiong et al. 2024 (ICLR) | https://github.com/MiaoXiong2320/llm-uncertainty |
| Yang et al. 2024 (arXiv:2412.14737) | https://github.com/danielyxyang/llm-verbalized-uq |
| Xue et al. 2025 (ACL Findings) | https://github.com/AmourWaltz/MlingConf |

---

## 2. インストールするツール一覧

### 2-1. コアライブラリ

| ツール | インストールコマンド | 用途 |
|---|---|---|
| torch | `pip install torch==2.2.2` | テンソル計算・ローカルモデル実行 |
| numpy | `pip install numpy==1.26.4` | 数値計算全般 |
| scipy | `pip install scipy==1.14.1` | 統計処理（Wilcoxon検定等） |
| pandas | `pip install pandas==2.2.2` | 結果CSV管理・集計 |

### 2-2. キャリブレーション指標（ECE・AUROC・Brier Score）

| ツール | インストールコマンド | 用途 | 論文採用実績 |
|---|---|---|---|
| **netcal** | `pip install netcal` | ECE計算・Reliability Diagram描画 | Xiong et al. 2024 |
| **scikit-learn** | `pip install scikit-learn` | AUROC（`roc_auc_score`）・Brier Score（`brier_score_loss`） | Xiong et al. 2024, Xue et al. 2025 |

**使用例:**
```python
from netcal.metrics import ECE
from netcal.presentation import ReliabilityDiagram
from sklearn.metrics import roc_auc_score, brier_score_loss

ece = ECE(bins=10)
ece_score = ece.measure(confidences, labels)          # 低いほど良
auroc = roc_auc_score(labels, confidences)            # 高いほど良
brier = brier_score_loss(labels, confidences)         # 低いほど良
```

> **注意**: Xue et al. 2025 は ECE を自前実装（10ビン）で計算しているが、
> 本研究では netcal で統一し比較可能性を確保する。

### 2-3. LLM API SDK

| ツール | インストールコマンド | 用途 | 論文採用実績 |
|---|---|---|---|
| **openai** | `pip install openai==1.43.0` | GPT-4o / GPT-5 API呼び出し | 全4論文 |
| **anthropic** | `pip install anthropic==0.33.0` | Claude Sonnet 4.6 API呼び出し | Tian et al. 2023 |
| **google-generativeai** | `pip install google-generativeai` | Gemini 2.0 Flash API呼び出し | （採用論文なし、本研究で追加） |
| **tiktoken** | `pip install tiktoken==0.7.0` | OpenAI トークン数カウント | Yang et al. 2024 |

### 2-4. データセット取得（HuggingFace）

| ツール | インストールコマンド | 用途 | 論文採用実績 |
|---|---|---|---|
| **datasets** | `pip install datasets==2.21.0` | MGSM / JCommonsenseQA / JMMLU / FLORES-200 取得 | Yang et al. 2024 |
| **transformers** | `pip install transformers==4.44.2` | tokenizer・オープンソースモデル読み込み | Xiong, Yang, Xue |
| **accelerate** | `pip install accelerate==0.33.0` | マルチGPU対応（Swallow等ローカル実行時） | Yang et al. 2024 |
| **huggingface-hub** | `pip install "huggingface-hub[hf_transfer]"` | モデル・データセットの高速ダウンロード | Yang et al. 2024 |

**データセット取得例:**
```python
from datasets import load_dataset

mgsm    = load_dataset("juletxara/mgsm", "ja")
jcqa    = load_dataset("sbintuitions/JCommonsenseQA")
jmmlu   = load_dataset("nlp-waseda/JMMLU")
flores  = load_dataset("facebook/flores", "jpn_Jpan-eng_Latn")
```

### 2-5. 翻訳評価（FLORES-200 ドメイン用）

| ツール | インストールコマンド | 用途 | 備考 |
|---|---|---|---|
| **unbabel-comet** | `pip install unbabel-comet` | 翻訳品質スコア（COMET）の計算 | 本研究で新規採用（先行4論文では未使用） |
| **rouge_score** | `pip install rouge_score` | ROUGE-L（参考値） | Xiong et al. 2024, Xue et al. 2025 |

**COMET使用例:**
```python
from comet import download_model, load_from_checkpoint

model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)
data = [{"src": src, "mt": hypothesis, "ref": reference}]
scores = model.predict(data, batch_size=8)
```

> COMET スコア閾値 θ は50文の人間二値判定で F1 最適化して決定（§5.5参照）。

### 2-6. 可視化

| ツール | インストールコマンド | 用途 | 論文採用実績 |
|---|---|---|---|
| **matplotlib** | `pip install matplotlib==3.9.2` | Reliability Diagram・棒グラフ等 | 全論文 |
| **seaborn** | `pip install seaborn` | ヒートマップ・統計図表 | 一般的 |
| **relplot** | `pip install relplot==1.0.3` | Reliability Plot 専用ライブラリ | Yang et al. 2024 |
| **adjustText** | `pip install adjustText` | 散布図のラベル重なり防止 | Xiong et al. 2024 |

### 2-7. ユーティリティ

| ツール | インストールコマンド | 用途 | 論文採用実績 |
|---|---|---|---|
| **tqdm** | `pip install tqdm==4.66.5` | API呼び出しのプログレスバー | Tian et al. 2023 |
| **wandb** | `pip install wandb` | 実験ログ・結果トラッキング | Xiong, Xue et al. |
| **fire** | `pip install fire` | CLIインターフェース自動生成 | Xiong, Xue et al. |
| **rich** | `pip install rich==13.7.1` | ターミナル出力の整形 | Tian et al. 2023 |

---

## 3. 一括インストールコマンド

```bash
# コアライブラリ
pip install torch==2.2.2 numpy==1.26.4 scipy==1.14.1 pandas==2.2.2

# キャリブレーション指標
pip install netcal scikit-learn

# LLM API SDK
pip install openai==1.43.0 anthropic==0.33.0 google-generativeai tiktoken==0.7.0

# HuggingFace エコシステム
pip install transformers==4.44.2 datasets==2.21.0 accelerate==0.33.0 "huggingface-hub[hf_transfer]"

# 翻訳評価
pip install unbabel-comet rouge_score

# 可視化
pip install matplotlib==3.9.2 seaborn relplot==1.0.3 adjustText

# ユーティリティ
pip install tqdm wandb fire rich
```

> **bitsandbytes について**: ローカルでオープンソースモデル（Swallow等）を量子化実行する場合に必要。
> GPU（CUDA）環境が前提のため、CPU環境では省略可。

---

## 4. Python バージョン

Yang et al. 2024 では **Python 3.12.4** を使用。
本研究でも Python 3.12 系を推奨。

```bash
# バージョン確認
python --version
```

---

## 5. 注意点・補足

### ECE 計算の非統一について
論文間で実装が混在（netcal vs 自前10ビン実装）。本研究では `netcal` に統一し、
先行研究との比較可能性を高める。

### Gemini SDK について
先行4論文は Gemini SDK（`google-generativeai`）を使用していない。
本研究で Gemini 2.0 Flash を追加するため新規採用。
最新 SDK では `google-generativeai` より `google-genai` が推奨される場合があるため、
実験開始前に公式ドキュメントでバージョンを確認すること。

### オープンソースモデル（Swallow・ELYZA・Qwen）について
- HuggingFace Hub からダウンロード（`transformers` + `accelerate`）
- GPU 環境またはローカルの計算資源が必要
- 量子化（4bit/8bit）には `bitsandbytes` が必要

### API キー管理
```bash
# .env ファイルで管理（.gitignore に追加すること）
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

---

## 参考リポジトリ

- [Xiong et al. 2024 - llm-uncertainty](https://github.com/MiaoXiong2320/llm-uncertainty)
- [Yang et al. 2024 - llm-verbalized-uq](https://github.com/danielyxyang/llm-verbalized-uq)
- [Xue et al. 2025 - MlingConf](https://github.com/AmourWaltz/MlingConf)
- [Tian et al. 2023 - boxing-gym](https://github.com/kanishkg/boxing-gym)
- [netcal PyPI](https://pypi.org/project/netcal/)
- [unbabel-comet PyPI](https://pypi.org/project/unbabel-comet/)
