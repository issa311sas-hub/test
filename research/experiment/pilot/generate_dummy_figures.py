"""
論文本体に挿入予定の「期待される図表」のダミー版を生成する。

目的:
- 論文を書く時にどういう図になるかを事前に可視化
- 指導教員との相談時に「こういう結果を出します」と説明する資料
- 実験前に figure 作成スクリプトを整備しておく

出力先: results/dummy_figures/
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import matplotlib.pyplot as plt
from calibration import compute_all, reliability_diagram_data

# 出力先
OUT_DIR = Path("results/dummy_figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 再現性のためシード固定
np.random.seed(2026)

# ===========================================================
# 想定結果のダミーデータ生成（論文執筆時のイメージ用）
# ===========================================================

MODELS = ["GPT-5", "Claude Sonnet 4.6", "Gemini 2.5", "Swallow"]
DOMAINS = ["Commonsense", "Math", "History", "Translation"]

# モデル別の「想定される ECE」のダミー値（仮説）
DUMMY_ECE_BY_MODEL = {
    "GPT-5": 0.08,
    "Claude Sonnet 4.6": 0.06,
    "Gemini 2.5": 0.12,
    "Swallow": 0.18,
}

# ドメイン別の想定 ECE（モデル × ドメイン）
DUMMY_ECE_MATRIX = np.array([
    # commonsense, math, history, translation
    [0.05, 0.10, 0.08, 0.09],  # GPT-5
    [0.04, 0.08, 0.06, 0.07],  # Claude
    [0.08, 0.15, 0.13, 0.11],  # Gemini
    [0.12, 0.22, 0.19, 0.18],  # Swallow
])


def simulate_confidence(n: int, base_acc: float, calibration_error: float, seed: int):
    """
    想定されるモデルの出力を模擬する。
    base_acc: そのモデルの平均正答率
    calibration_error: 過信の度合い（負値なら過小評価）
    """
    rng = np.random.default_rng(seed)
    # 正答を先に決める
    correct = (rng.random(n) < base_acc).astype(int)
    # 信頼度は正答率に近いが、過信方向にバイアス
    confidences = np.clip(
        base_acc + calibration_error + rng.normal(0, 0.15, n),
        0.0, 1.0
    )
    # 正解だと信頼度を上げる、誤答だと少し下げる（多少のシグナル）
    confidences = np.clip(confidences + 0.1 * (correct - 0.5), 0.0, 1.0)
    return confidences, correct


# ===========================================================
# 図5-1: モデル別 Reliability Diagram（2x2）
# ===========================================================

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
fig.suptitle("Figure 5-1: Model-wise Reliability Diagram (Dummy)",
             fontsize=14, y=1.00)

for i, model in enumerate(MODELS):
    ax = axes[i // 2, i % 2]
    ece_target = DUMMY_ECE_BY_MODEL[model]
    base_acc = 0.75 - (i * 0.08)  # 想定正答率
    confidences, correct = simulate_confidence(
        n=200, base_acc=base_acc, calibration_error=ece_target, seed=42 + i
    )
    data = reliability_diagram_data(confidences, correct, n_bins=10)
    metrics = compute_all(confidences, correct)

    # 理想直線
    ax.plot([0, 1], [0, 1], "k--", label="Perfect")
    # モデル曲線
    valid = [j for j, a in enumerate(data["accuracies"]) if not np.isnan(a)]
    ax.plot(
        [data["mean_confidences"][j] for j in valid],
        [data["accuracies"][j] for j in valid],
        "o-", color="steelblue", label=model
    )
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"{model}\nECE={metrics.ece:.3f}, Brier={metrics.brier:.3f}")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
out_path = OUT_DIR / "fig5-1_model_reliability.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")


# ===========================================================
# 図5-2: ドメイン別 ECE の棒グラフ（モデル別にグループ化）
# ===========================================================

fig, ax = plt.subplots(figsize=(10, 6))
n_models = len(MODELS)
n_domains = len(DOMAINS)
x = np.arange(n_domains)
width = 0.18
colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"]

for i, model in enumerate(MODELS):
    offset = (i - n_models / 2 + 0.5) * width
    ax.bar(x + offset, DUMMY_ECE_MATRIX[i], width, label=model, color=colors[i])

ax.set_xlabel("Domain")
ax.set_ylabel("Expected Calibration Error (ECE)")
ax.set_title("Figure 5-2: ECE by Model and Domain (Dummy)")
ax.set_xticks(x)
ax.set_xticklabels(DOMAINS)
ax.legend(loc="upper left")
ax.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
out_path = OUT_DIR / "fig5-2_ece_by_domain.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")


# ===========================================================
# 図5-3: プロンプト方式別 ECE の比較
# ===========================================================

PROMPT_CONDITIONS = ["0-100 Integer", "1-5 Scale", "Percentage", "Verbal"]
DUMMY_ECE_BY_PROMPT = np.array([
    [0.08, 0.10, 0.09, 0.13],  # GPT-5
    [0.06, 0.09, 0.07, 0.11],  # Claude
    [0.12, 0.14, 0.13, 0.16],  # Gemini
    [0.18, 0.21, 0.19, 0.24],  # Swallow
])

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(PROMPT_CONDITIONS))
for i, model in enumerate(MODELS):
    offset = (i - n_models / 2 + 0.5) * width
    ax.bar(x + offset, DUMMY_ECE_BY_PROMPT[i], width, label=model, color=colors[i])

ax.set_xlabel("Prompt Format")
ax.set_ylabel("Expected Calibration Error (ECE)")
ax.set_title("Figure 5-3: ECE by Prompt Format (Dummy)")
ax.set_xticks(x)
ax.set_xticklabels(PROMPT_CONDITIONS)
ax.legend(loc="upper left")
ax.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
out_path = OUT_DIR / "fig5-3_ece_by_prompt.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")


# ===========================================================
# 図5-4: 日英の Reliability Diagram 比較（GPT-5のみ）
# ===========================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Figure 5-4: Japanese vs English Calibration (GPT-5, Dummy)",
             fontsize=14, y=1.03)

for idx, (lang, ece_target) in enumerate([("Japanese", 0.08), ("English", 0.05)]):
    ax = axes[idx]
    confidences, correct = simulate_confidence(
        n=200, base_acc=0.78, calibration_error=ece_target, seed=100 + idx
    )
    data = reliability_diagram_data(confidences, correct, n_bins=10)
    metrics = compute_all(confidences, correct)

    ax.plot([0, 1], [0, 1], "k--", label="Perfect")
    valid = [j for j, a in enumerate(data["accuracies"]) if not np.isnan(a)]
    ax.plot(
        [data["mean_confidences"][j] for j in valid],
        [data["accuracies"][j] for j in valid],
        "o-", color="steelblue", label=lang
    )
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"{lang}\nECE={metrics.ece:.3f}")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
out_path = OUT_DIR / "fig5-4_lang_comparison.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")

# ===========================================================
# 表5-1: モデル別の calibration metrics（テキストで出力）
# ===========================================================

print("\n" + "=" * 60)
print("Table 5-1: Calibration metrics by model (Dummy)")
print("=" * 60)
print(f"{'Model':<25} {'ECE':>8} {'Brier':>8} {'AUROC':>8} {'Acc':>8}")
print("-" * 60)
for i, model in enumerate(MODELS):
    ece_target = DUMMY_ECE_BY_MODEL[model]
    base_acc = 0.75 - (i * 0.08)
    confidences, correct = simulate_confidence(
        n=200, base_acc=base_acc, calibration_error=ece_target, seed=42 + i
    )
    m = compute_all(confidences, correct)
    auroc_str = f"{m.auroc:.3f}" if m.auroc else "N/A"
    print(f"{model:<25} {m.ece:>8.3f} {m.brier:>8.3f} "
          f"{auroc_str:>8} {m.mean_accuracy:>8.2%}")
print("=" * 60)

print(f"\n全ダミー図表を {OUT_DIR}/ に保存しました")
print("これは論文本体に挿入する figure の雛形です。")
print("実際の結果は実験後に上書きされます。")
