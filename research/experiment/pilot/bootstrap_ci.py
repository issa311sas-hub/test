"""
方式間の差が誤差範囲かどうかを、ブートストラップ法で検証する。

なぜ必要か:
  パイロットは 250 問・単一試行なので、「Verb.2S の ECE が Verb.1S より
  0.03 低い」が本当の差なのか、たまたま選んだ 250 問による揺らぎなのかが
  分からない。問題集合を復元抽出で作り直して指標を計算し直すことで、
  各指標の 95% 信頼区間と、方式間の差の信頼区間を得る。

対応のあるブートストラップ:
  3方式はまったく同じ 250 問に対して実行されている。問題ごとに 3方式の
  結果を組にして同時に再抽出する（対応のある設計）。方式ごとに独立に
  再抽出すると、問題の難易度差が差分の分散に二重に乗り、信頼区間が
  不当に広くなる。

差の読み方:
  差の 95% 信頼区間が 0 をまたがなければ、その差は偶然では説明しにくい。
  0 をまたぐ場合、「この問題数では差を主張できない」と報告する。

使い方:
  python bootstrap_ci.py                    # 既定のファイル名で実行
  python bootstrap_ci.py --n-boot 10000     # 反復回数を増やす
  python bootstrap_ci.py --out results/bootstrap.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from calibration import compute_ece, compute_brier, compute_auroc, compute_murphy_decomposition
from compare_methods import SERIES, _as_bool

N_BINS = 10

# 指標名 → (計算関数, 大きいほど良いか)
METRICS = {
    "ECE": (lambda c, y: compute_ece(c, y, n_bins=N_BINS), False),
    "Brier": (lambda c, y: compute_brier(c, y), False),
    "AUROC": (lambda c, y: compute_auroc(c, y), True),
    "REL": (lambda c, y: compute_murphy_decomposition(c, y, n_bins=N_BINS).rel, False),
    "RES": (lambda c, y: compute_murphy_decomposition(c, y, n_bins=N_BINS).res, True),
    "Accuracy": (lambda c, y: float(np.mean(y)), True),
}


def load_paired(paths: dict[str, str]) -> tuple[list[str], dict[str, np.ndarray], dict[str, np.ndarray]]:
    """3方式を問題 id で突き合わせ、全方式で確信度が取れた問題だけを残す。"""
    import csv

    per_method: dict[str, dict[str, tuple[float, int]]] = {}
    for key, label, color, marker in SERIES:
        path = Path(paths[key])
        if not path.exists():
            raise FileNotFoundError(f"ファイルがありません: {path}")
        table: dict[str, tuple[float, int]] = {}
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                raw = row.get("confidence", "")
                if raw in ("", None):
                    continue
                try:
                    conf = float(raw)
                except ValueError:
                    continue
                table[row["id"]] = (conf, _as_bool(row.get("correct")))
        per_method[key] = table

    common = set.intersection(*(set(t) for t in per_method.values()))
    ids = sorted(common)
    if not ids:
        raise ValueError("3方式すべてで確信度が取れた共通の問題がありません。")

    conf = {k: np.array([per_method[k][i][0] for i in ids]) for k in per_method}
    corr = {k: np.array([per_method[k][i][1] for i in ids]) for k in per_method}
    return ids, conf, corr


def bootstrap(
    conf: dict[str, np.ndarray],
    corr: dict[str, np.ndarray],
    n_boot: int,
    seed: int,
) -> dict[str, dict[str, np.ndarray]]:
    """指標ごと・方式ごとのブートストラップ分布を返す。"""
    rng = np.random.default_rng(seed)
    n = len(next(iter(conf.values())))
    keys = list(conf)
    dists: dict[str, dict[str, list[float]]] = {
        m: {k: [] for k in keys} for m in METRICS
    }

    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)  # 全方式で同じ添字（対応のある再抽出）
        for m, (fn, _) in METRICS.items():
            for k in keys:
                c, y = conf[k][idx], corr[k][idx]
                try:
                    v = fn(c, y)
                except Exception:
                    v = None
                # AUROC は再抽出で全問正答/全問誤答になると None を返す
                dists[m][k].append(float("nan") if v is None else float(v))

    return {m: {k: np.array(v) for k, v in d.items()} for m, d in dists.items()}


def ci(values: np.ndarray, alpha: float = 0.05) -> tuple[float, float, int]:
    """パーセンタイル法の信頼区間。NaN は除外し、有効件数も返す。"""
    v = values[~np.isnan(values)]
    if len(v) == 0:
        return float("nan"), float("nan"), 0
    lo = float(np.percentile(v, 100 * alpha / 2))
    hi = float(np.percentile(v, 100 * (1 - alpha / 2)))
    return lo, hi, len(v)


def main() -> int:
    p = argparse.ArgumentParser(description="方式間の差をブートストラップで検証する")
    p.add_argument("--verb1s", default="results/mgsm_verb1s.csv")
    p.add_argument("--verb2s", default="results/mgsm_verb2s.csv")
    p.add_argument("--ling1s", default="results/mgsm_ling1s_rescored.csv")
    p.add_argument("--n-boot", type=int, default=5000, help="反復回数（既定 5000）")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="results/bootstrap.md")
    args = p.parse_args()

    paths = {"verb_1s": args.verb1s, "verb_2s": args.verb2s, "ling_1s": args.ling1s}
    labels = {k: lab for k, lab, _, _ in SERIES}

    try:
        ids, conf, corr = load_paired(paths)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"共通問題数: {len(ids)} 問（3方式すべてで確信度が取れたもの）")
    print(f"ブートストラップ: {args.n_boot} 回")
    dists = bootstrap(conf, corr, args.n_boot, args.seed)

    lines = [
        "# ブートストラップ信頼区間（対応のある再抽出）",
        "",
        f"- 共通問題数: {len(ids)}",
        f"- 反復回数: {args.n_boot}",
        f"- 乱数シード: {args.seed}",
        "- 方法: 問題を復元抽出し、3方式に同じ添字を適用（対応のある設計）",
        "- 区間: パーセンタイル法による 95% 信頼区間",
        "",
        "## 各方式の指標",
        "",
        "| 指標 | 方式 | 点推定 | 95% CI |",
        "|---|---|---|---|",
    ]
    for m in METRICS:
        for k in conf:
            point = METRICS[m][0](conf[k], corr[k])
            point = float("nan") if point is None else float(point)
            lo, hi, _ = ci(dists[m][k])
            lines.append(
                f"| {m} | {labels[k]} | {point:.4f} | [{lo:.4f}, {hi:.4f}] |"
            )

    lines += [
        "",
        "## 方式間の差",
        "",
        "差の 95% CI が 0 をまたぐ場合、この問題数では差を主張できない。",
        "",
        "| 指標 | 比較 | 差の点推定 | 95% CI | 有効反復 | 0を含むか |",
        "|---|---|---|---|---|---|",
    ]
    keys = list(conf)
    verdicts: list[tuple[str, str, bool]] = []
    low_valid: list[tuple[str, str, int]] = []
    for m in METRICS:
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                d = dists[m][a] - dists[m][b]
                lo, hi, n_valid = ci(d)
                pa = METRICS[m][0](conf[a], corr[a])
                pb = METRICS[m][0](conf[b], corr[b])
                point = float("nan") if (pa is None or pb is None) else float(pa) - float(pb)
                spans_zero = not (lo > 0 or hi < 0)
                mark = "含む（差を主張できない）" if spans_zero else "**含まない**"
                lines.append(
                    f"| {m} | {labels[a]} − {labels[b]} | {point:+.4f} | "
                    f"[{lo:+.4f}, {hi:+.4f}] | {n_valid}/{args.n_boot} | {mark} |"
                )
                if n_valid < args.n_boot:
                    low_valid.append((m, f"{labels[a]} vs {labels[b]}", n_valid))
                verdicts.append((m, f"{labels[a]} vs {labels[b]}", spans_zero))

    inconclusive = [v for v in verdicts if v[2]]
    lines += [
        "",
        "## まとめ",
        "",
        f"- 比較 {len(verdicts)} 件中 {len(verdicts) - len(inconclusive)} 件で "
        "差の CI が 0 を含まなかった。",
    ]
    if inconclusive:
        lines.append("- 差を主張できない組み合わせ:")
        for m, pair, _ in inconclusive:
            lines.append(f"  - {m}: {pair}")
    if low_valid:
        lines.append(
            "- 一部の反復で指標が計算できず、下記の区間は反復回数より少ない"
            "標本から求めている（AUROC は再抽出で全問正答/全問誤答になると"
            "計算不能になる）:"
        )
        for m, pair, nv in low_valid:
            lines.append(f"  - {m}: {pair} — 有効 {nv}/{args.n_boot} 回")
    lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"保存: {out}")

    print("\n差の検定結果（0 を含む＝差を主張できない）:")
    for m, pair, spans in verdicts:
        if spans:
            print(f"  [差を主張できない] {m}: {pair}")
    if not inconclusive:
        print("  すべての比較で差の CI が 0 を含みませんでした。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
