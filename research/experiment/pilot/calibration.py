"""
Calibration 指標の計算

- ECE (Expected Calibration Error)
- Brier Score
- AUROC
- Reliability Diagram 用データ
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class CalibrationMetrics:
    ece: float
    brier: float
    auroc: float | None
    mean_confidence: float
    mean_accuracy: float
    n: int


def compute_ece(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> float:
    """
    Expected Calibration Error (ECE) を計算する。

    confidences: 0〜1 の配列
    correct: 0/1 の配列
    n_bins: ビンの数（デフォルト10）
    """
    assert confidences.shape == correct.shape
    assert np.all((confidences >= 0) & (confidences <= 1)), "confidences must be in [0, 1]"

    n = len(confidences)
    if n == 0:
        return 0.0

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        lo = bin_edges[i]
        hi = bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (confidences >= lo) & (confidences <= hi)
        else:
            mask = (confidences >= lo) & (confidences < hi)

        bin_n = mask.sum()
        if bin_n == 0:
            continue
        bin_conf = confidences[mask].mean()
        bin_acc = correct[mask].mean()
        ece += (bin_n / n) * abs(bin_conf - bin_acc)

    return float(ece)


def compute_brier(confidences: np.ndarray, correct: np.ndarray) -> float:
    """Brier Score = mean((confidence - correct)^2)"""
    return float(np.mean((confidences - correct.astype(float)) ** 2))


def compute_auroc(confidences: np.ndarray, correct: np.ndarray) -> float | None:
    """
    AUROC: 信頼度で正答/誤答をどれだけ識別できるか。
    全問正答または全問誤答の場合は計算不能なので None を返す。
    """
    pos = confidences[correct == 1]
    neg = confidences[correct == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    # ノンパラ手法: Mann-Whitney U の正規化
    comparisons = 0.0
    for p in pos:
        comparisons += (neg < p).sum() + 0.5 * (neg == p).sum()
    return float(comparisons / (len(pos) * len(neg)))


def compute_all(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> CalibrationMetrics:
    return CalibrationMetrics(
        ece=compute_ece(confidences, correct, n_bins=n_bins),
        brier=compute_brier(confidences, correct),
        auroc=compute_auroc(confidences, correct),
        mean_confidence=float(np.mean(confidences)),
        mean_accuracy=float(np.mean(correct)),
        n=len(confidences),
    )


def reliability_diagram_data(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> dict:
    """
    Reliability Diagram 用のビン別データを返す。
    matplotlib等で可視化する時に利用する。
    """
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    accuracies = []
    counts = []
    mean_confidences = []
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        if i == n_bins - 1:
            mask = (confidences >= lo) & (confidences <= hi)
        else:
            mask = (confidences >= lo) & (confidences < hi)
        n = int(mask.sum())
        counts.append(n)
        if n > 0:
            accuracies.append(float(correct[mask].mean()))
            mean_confidences.append(float(confidences[mask].mean()))
        else:
            accuracies.append(float("nan"))
            mean_confidences.append(float("nan"))
    return {
        "bin_centers": centers.tolist(),
        "mean_confidences": mean_confidences,
        "accuracies": accuracies,
        "counts": counts,
    }


@dataclass
class MurphyDecomposition:
    """Murphy 分解: BS = REL - RES + UNC"""
    rel: float          # Reliability (低いほど良)
    res: float          # Resolution (高いほど良)
    unc: float          # Uncertainty (データ固有の定数)
    brier: float        # = REL - RES + UNC で検算可能
    n_bins: int
    bin_counts: list[int]
    bin_mean_conf: list[float]
    bin_mean_acc: list[float]


def compute_murphy_decomposition(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> MurphyDecomposition:
    """
    Murphy 分解 (Murphy 1973): BS = REL − RES + UNC

    REL = Σₖ (nₖ/n) × (f̄ₖ − ōₖ)²   ← 低いほど良 (0 = 完璧なキャリブレーション)
    RES = Σₖ (nₖ/n) × (ōₖ − ō)²    ← 高いほど良 (大きいほど識別能力が高い)
    UNC = ō × (1 − ō)                ← データ固有の定数

    参照: Bröcker (2009) QJRMS, Ferro & Fricker (2012) arXiv:1303.6182
    """
    assert confidences.shape == correct.shape
    n = len(confidences)
    if n == 0:
        return MurphyDecomposition(rel=0.0, res=0.0, unc=0.0, brier=0.0,
                                   n_bins=n_bins, bin_counts=[], bin_mean_conf=[], bin_mean_acc=[])

    o_bar = float(np.mean(correct))  # 全体正答率 (UNC の基準)
    unc = o_bar * (1.0 - o_bar)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    rel = 0.0
    res = 0.0
    bin_counts = []
    bin_mean_conf_list = []
    bin_mean_acc_list = []

    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (confidences >= lo) & (confidences <= hi if i == n_bins - 1 else confidences < hi)
        nk = int(mask.sum())
        bin_counts.append(nk)
        if nk == 0:
            bin_mean_conf_list.append(float("nan"))
            bin_mean_acc_list.append(float("nan"))
            continue
        f_bar_k = float(confidences[mask].mean())  # ビン内平均確信度
        o_bar_k = float(correct[mask].mean())       # ビン内正答率
        bin_mean_conf_list.append(f_bar_k)
        bin_mean_acc_list.append(o_bar_k)
        weight = nk / n
        rel += weight * (f_bar_k - o_bar_k) ** 2
        res += weight * (o_bar_k - o_bar) ** 2

    brier = rel - res + unc  # 検算用
    return MurphyDecomposition(
        rel=rel, res=res, unc=unc, brier=brier,
        n_bins=n_bins, bin_counts=bin_counts,
        bin_mean_conf=bin_mean_conf_list, bin_mean_acc=bin_mean_acc_list,
    )


@dataclass
class FullMetrics:
    calibration: CalibrationMetrics
    murphy: MurphyDecomposition


def compute_full(
    confidences: np.ndarray, correct: np.ndarray, n_bins: int = 10
) -> FullMetrics:
    """ECE / Brier / AUROC + Murphy 分解をまとめて計算する"""
    return FullMetrics(
        calibration=compute_all(confidences, correct, n_bins=n_bins),
        murphy=compute_murphy_decomposition(confidences, correct, n_bins=n_bins),
    )


if __name__ == "__main__":
    # 動作確認: 完全に calibrated な仮想データ
    np.random.seed(42)
    n = 1000
    confidences = np.random.rand(n)
    correct = (np.random.rand(n) < confidences).astype(int)
    metrics = compute_all(confidences, correct)
    print("Synthetic calibrated data:")
    print(f"  ECE: {metrics.ece:.4f}")
    print(f"  Brier: {metrics.brier:.4f}")
    print(f"  AUROC: {metrics.auroc:.4f}")
    print(f"  Mean Conf: {metrics.mean_confidence:.4f}")
    print(f"  Mean Acc: {metrics.mean_accuracy:.4f}")
