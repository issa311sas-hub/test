"""
結果の可視化スクリプト

使い方:
  $ python visualize.py --input results/mock_run.csv --output results/diagram.png

Reliability Diagram を生成する。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def load_results(path: str) -> tuple[list[float], list[int], list[str]]:
    confidences = []
    correct = []
    domains = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("confidence") and row["confidence"] != "":
                try:
                    confidences.append(float(row["confidence"]))
                    correct.append(int(row["correct"]))
                    domains.append(row.get("domain", ""))
                except ValueError:
                    continue
    return confidences, correct, domains


def plot_reliability_diagram(confidences, correct, output_path, title="Reliability Diagram"):
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        from calibration import reliability_diagram_data, compute_all
    except ImportError as e:
        print(f"必要なパッケージがインストールされていません: {e}")
        print("pip install matplotlib numpy を実行してください")
        return

    confidences = np.array(confidences)
    correct = np.array(correct)

    data = reliability_diagram_data(confidences, correct, n_bins=10)
    metrics = compute_all(confidences, correct)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 左: Reliability Diagram
    bin_centers = data["bin_centers"]
    accuracies = data["accuracies"]
    mean_confidences = data["mean_confidences"]

    ax1.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    valid = [i for i, a in enumerate(accuracies) if not (a != a)]  # NaN除外
    ax1.plot(
        [mean_confidences[i] for i in valid],
        [accuracies[i] for i in valid],
        "o-", label="Model", color="steelblue"
    )
    ax1.set_xlabel("Confidence")
    ax1.set_ylabel("Accuracy")
    ax1.set_title(f"{title}\nECE={metrics.ece:.3f}, Brier={metrics.brier:.3f}")
    ax1.set_xlim([0, 1])
    ax1.set_ylim([0, 1])
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 右: Confidence Histogram
    ax2.hist(confidences, bins=10, range=(0, 1), color="coral", alpha=0.7, edgecolor="black")
    ax2.set_xlabel("Confidence")
    ax2.set_ylabel("Count")
    ax2.set_title("Confidence Distribution")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    # 出力ディレクトリを作成
    import os
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")
    print(f"  N = {metrics.n}")
    print(f"  Accuracy = {metrics.mean_accuracy:.2%}")
    print(f"  Mean Confidence = {metrics.mean_confidence:.2%}")
    print(f"  ECE = {metrics.ece:.4f}")
    print(f"  Brier = {metrics.brier:.4f}")
    if metrics.auroc is not None:
        print(f"  AUROC = {metrics.auroc:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="結果CSVファイル")
    parser.add_argument("--output", required=True, help="出力画像ファイル")
    parser.add_argument("--title", default="Reliability Diagram", help="図のタイトル")
    args = parser.parse_args()

    confidences, correct, domains = load_results(args.input)
    if not confidences:
        print("有効なデータが見つかりませんでした")
        return

    plot_reliability_diagram(confidences, correct, args.output, title=args.title)


if __name__ == "__main__":
    main()
