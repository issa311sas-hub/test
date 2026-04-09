"""
calibration.py の単体テスト

実行方法:
  $ python test_calibration.py
"""

import numpy as np
from calibration import compute_ece, compute_brier, compute_auroc, compute_all


def approx_equal(a, b, tol=1e-6):
    return abs(a - b) < tol


def test(description, actual, expected, tol=1e-6):
    if isinstance(expected, float):
        ok = approx_equal(actual, expected, tol)
    else:
        ok = actual == expected
    mark = "OK  " if ok else "FAIL"
    print(f"[{mark}] {description}")
    if not ok:
        print(f"       expected: {expected}")
        print(f"       actual:   {actual}")
    return ok


def main():
    results = []

    # ===== 完全 calibrated =====
    # 全問題が信頼度1.0で、全問正解 → ECE = 0
    conf = np.array([1.0, 1.0, 1.0, 1.0])
    correct = np.array([1, 1, 1, 1])
    results.append(test("全1.0・全正解 → ECE=0", compute_ece(conf, correct), 0.0))
    results.append(test("全1.0・全正解 → Brier=0", compute_brier(conf, correct), 0.0))

    # ===== 完全 miscalibrated =====
    # 全問題が信頼度1.0で、全問不正解 → ECE = 1
    conf = np.array([1.0, 1.0, 1.0, 1.0])
    correct = np.array([0, 0, 0, 0])
    results.append(test("全1.0・全不正解 → ECE=1", compute_ece(conf, correct), 1.0))
    results.append(test("全1.0・全不正解 → Brier=1", compute_brier(conf, correct), 1.0))

    # ===== 中程度の calibration =====
    # 信頼度0.5で、正答率0.5 → 完璧
    conf = np.full(100, 0.5)
    correct = np.concatenate([np.ones(50), np.zeros(50)])
    results.append(test("0.5・正答率50% → ECE=0", compute_ece(conf, correct), 0.0))

    # ===== Brier Score =====
    # 信頼度0.5 ・ 全正解 → Brier = 0.25
    conf = np.full(10, 0.5)
    correct = np.ones(10, dtype=int)
    results.append(test("0.5・全正解 → Brier=0.25", compute_brier(conf, correct), 0.25))

    # ===== AUROC =====
    # 高信頼度で正解、低信頼度で不正解 → AUROC=1.0
    conf = np.array([0.9, 0.8, 0.2, 0.1])
    correct = np.array([1, 1, 0, 0])
    results.append(test("完璧な識別 → AUROC=1.0", compute_auroc(conf, correct), 1.0))

    # 逆転: 高信頼度で不正解、低信頼度で正解 → AUROC=0.0
    conf = np.array([0.9, 0.8, 0.2, 0.1])
    correct = np.array([0, 0, 1, 1])
    results.append(test("逆転 → AUROC=0.0", compute_auroc(conf, correct), 0.0))

    # ランダムに近い → AUROC=0.5
    conf = np.array([0.5, 0.5, 0.5, 0.5])
    correct = np.array([1, 0, 1, 0])
    results.append(test("同信頼度・半正解 → AUROC=0.5", compute_auroc(conf, correct), 0.5))

    # 全問正解の場合 → AUROC計算不能
    conf = np.array([0.8, 0.9, 0.7])
    correct = np.array([1, 1, 1])
    results.append(test("全問正解 → AUROC=None", compute_auroc(conf, correct), None))

    # ===== compute_all の統合 =====
    conf = np.array([0.9, 0.8, 0.3, 0.2])
    correct = np.array([1, 1, 0, 0])
    metrics = compute_all(conf, correct)
    results.append(test("統合: N", metrics.n, 4))
    results.append(test("統合: mean_conf", metrics.mean_confidence, 0.55))
    results.append(test("統合: mean_acc", metrics.mean_accuracy, 0.5))
    results.append(test("統合: AUROC=1.0", metrics.auroc, 1.0))

    # ===== サマリー =====
    n_passed = sum(results)
    n_total = len(results)
    print(f"\n{'=' * 40}")
    print(f"結果: {n_passed}/{n_total} passed")
    print(f"{'=' * 40}")

    return 0 if n_passed == n_total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
