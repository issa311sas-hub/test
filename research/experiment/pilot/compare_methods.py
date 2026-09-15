"""
3方式（Verb.1S / Verb.2S / Ling.1S）の比較図と結果表を生成する。

出力:
  figures/fig1_reliability.png   信頼度ダイアグラム（3方式重ね書き）
  figures/fig2_confidence.png    確信度の分布（3方式の小倍数）
  figures/fig3_metrics.png       ECE / Brier / AUROC の比較
  results/comparison.md          比較表（Markdown）

使い方:
  python compare_methods.py \
      --verb1s results/mgsm_verb1s.csv \
      --verb2s results/mgsm_verb2s.csv \
      --ling1s results/mgsm_ling1s_rescored.csv

注意: 図は発表スライド（印刷・プロジェクタ）用の静的PNG。日本語フォントが
無い環境でも崩れないよう、図中のラベルは英語で統一している。
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from calibration import compute_full, reliability_diagram_data

# 系列色（検証済みカテゴリカル配色の slot 1-3）。
# 3系列は全ペアで CVD 判別可能。aqua は明るい背景とのコントラストが 3:1 を
# 下回るため、色だけに頼らないよう直接ラベルとマーカー形状を必ず併用する。
SERIES = [
    ("verb_1s", "Verb.1S", "#2a78d6", "o"),
    ("verb_2s", "Verb.2S", "#eb6834", "s"),
    ("ling_1s", "Ling.1S", "#1baf7a", "^"),
]

TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#d8d7d2"
N_BINS = 10


@dataclass
class MethodResult:
    key: str
    label: str
    color: str
    marker: str
    conf: np.ndarray
    correct: np.ndarray
    n_rows: int          # CSV の全行数
    n_scored: int        # 確信度が取れて指標計算に使えた行数
    n_correct_all: int   # 全行のうち正答した数


def _as_bool(raw: str | None) -> int:
    """correct 列を 0/1 にする。

    run_pilot.py は int で書くが、Excel 等で開いて保存し直すと "1.0" や
    "TRUE" になることがある。読めない値は 0（誤答）扱いにする。
    """
    if raw is None:
        return 0
    s = str(raw).strip().lower()
    if s in ("true", "yes"):
        return 1
    if s in ("", "false", "no"):
        return 0
    try:
        return 1 if float(s) != 0 else 0
    except ValueError:
        return 0


def load(path: Path, key: str, label: str, color: str, marker: str) -> MethodResult:
    confs: list[float] = []
    corrs: list[int] = []
    n_rows = 0
    n_correct_all = 0
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n_rows += 1
            is_correct = _as_bool(row.get("correct"))
            n_correct_all += is_correct
            raw = row.get("confidence", "")
            if raw == "" or raw is None:
                continue
            try:
                confs.append(float(raw))
            except ValueError:
                continue
            corrs.append(is_correct)
    if not confs:
        raise ValueError(f"{path} に確信度のある行が1つもありません。")
    return MethodResult(
        key=key, label=label, color=color, marker=marker,
        conf=np.array(confs), correct=np.array(corrs),
        n_rows=n_rows, n_scored=len(confs), n_correct_all=n_correct_all,
    )


def _style(ax) -> None:
    """軸・グリッドを後退させ、データを前に出す。"""
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def fig_reliability(results: list[MethodResult], out: Path) -> None:
    """信頼度ダイアグラム: 対角線が完全較正。下に外れれば自信過剰。"""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1.4,
            color=TEXT_SECONDARY, alpha=0.6, zorder=1)
    # 曲線は対角線の上側に集まるので、ラベルは下側の空白に置いて引き出し線で結ぶ
    ax.annotate("Perfect calibration", xy=(0.42, 0.42), xytext=(0.60, 0.22),
                fontsize=9, color=TEXT_SECONDARY,
                arrowprops=dict(arrowstyle="-", color=TEXT_SECONDARY,
                                linewidth=0.8, alpha=0.7))

    for r in results:
        d = reliability_diagram_data(r.conf, r.correct, n_bins=N_BINS)
        xs, ys = [], []
        for mc, acc in zip(d["mean_confidences"], d["accuracies"]):
            if not (np.isnan(mc) or np.isnan(acc)):
                xs.append(mc)
                ys.append(acc)
        ax.plot(xs, ys, linewidth=2.0, color=r.color, marker=r.marker,
                markersize=8, markeredgecolor="white", markeredgewidth=1.4,
                zorder=3, label=r.label)
    # 3系列の終点は高確信度側に集まるため、直接ラベルは必ず重なる。
    # 代わりにマーカー形状（○/□/△）を色と独立した識別子として使い、
    # 凡例にも同じ形状を出すことで、色だけに頼らずに読めるようにしている。

    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Confidence", color=TEXT_SECONDARY, fontsize=10)
    ax.set_ylabel("Accuracy", color=TEXT_SECONDARY, fontsize=10)
    ax.set_title("Reliability diagram (MGSM-ja, n=250)",
                 color=TEXT_PRIMARY, fontsize=13, fontweight="bold", pad=12)
    _style(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    _save(fig, out)


def fig_confidence(results: list[MethodResult], out: Path) -> None:
    """確信度の分布。重ね書きは読めないので小倍数にする。"""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(results), figsize=(11.5, 3.6), sharey=True)
    for ax, r in zip(np.atleast_1d(axes), results):
        ax.hist(r.conf, bins=np.linspace(0, 1, N_BINS + 1),
                color=r.color, edgecolor="white", linewidth=1.2)
        ax.axvline(float(r.correct.mean()), color=TEXT_SECONDARY,
                   linestyle="--", linewidth=1.2)
        ax.annotate(f"accuracy {r.correct.mean():.0%}",
                    xy=(float(r.correct.mean()), 0.96),
                    xycoords=("data", "axes fraction"),
                    xytext=(-4, 0), textcoords="offset points",
                    ha="right", va="top", fontsize=8, color=TEXT_SECONDARY)
        ax.set_title(r.label, color=TEXT_PRIMARY, fontsize=11, fontweight="bold")
        ax.set_xlabel("Confidence", color=TEXT_SECONDARY, fontsize=9)
        ax.set_xlim(0, 1)
        _style(ax)
    np.atleast_1d(axes)[0].set_ylabel("Questions", color=TEXT_SECONDARY, fontsize=9)
    fig.suptitle("Confidence distribution by elicitation method",
                 color=TEXT_PRIMARY, fontsize=13, fontweight="bold", y=1.04)
    _save(fig, out)


def fig_metrics(results: list[MethodResult], metrics: dict, out: Path) -> None:
    """指標比較。尺度が違うので1枚に混ぜず、指標ごとにパネルを分ける。"""
    import matplotlib.pyplot as plt

    panels = [
        ("ece", "ECE  (lower is better)", lambda m: m.calibration.ece),
        ("brier", "Brier score  (lower is better)", lambda m: m.calibration.brier),
        ("auroc", "AUROC  (higher is better)", lambda m: m.calibration.auroc),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
    for ax, (_, title, get) in zip(axes, panels):
        vals, labels, colors = [], [], []
        for r in results:
            v = get(metrics[r.key])
            vals.append(float("nan") if v is None else float(v))
            labels.append(r.label)
            colors.append(r.color)
        bars = ax.bar(labels, vals, color=colors, width=0.62)
        for b, v in zip(bars, vals):
            if not np.isnan(v):
                ax.annotate(f"{v:.3f}", xy=(b.get_x() + b.get_width() / 2, v),
                            xytext=(0, 4), textcoords="offset points",
                            ha="center", fontsize=10, color=TEXT_PRIMARY,
                            fontweight="bold")
        ax.set_title(title, color=TEXT_PRIMARY, fontsize=11, fontweight="bold")
        finite = [v for v in vals if not np.isnan(v)]
        if finite:
            ax.set_ylim(0, max(finite) * 1.28)
        else:
            # AUROC は全問正答／全問誤答だと None になる。その場合は
            # 空のパネルを描いて「計算不能」と明示する（落とさない）。
            ax.set_ylim(0, 1)
            ax.annotate("N/A", xy=(0.5, 0.5), xycoords="axes fraction",
                        ha="center", va="center", fontsize=14,
                        color=TEXT_SECONDARY)
        _style(ax)
        ax.grid(axis="x", visible=False)
    _save(fig, out)


def _save(fig, out: Path) -> None:
    import matplotlib.pyplot as plt

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  保存: {out}")


def write_markdown(results: list[MethodResult], metrics: dict, out: Path) -> None:
    lines = [
        "# 3方式比較（MGSM 日本語版 250問）",
        "",
        "- モデル: claude-sonnet-4-6（temperature=0.0）",
        "- データ: MGSM 日本語版 250問（Shi et al. 2023, ICLR）",
        "- ドメイン: 数学（自由回答・数値）",
        f"- ECE のビン数: {N_BINS}",
        "- 生成: `compare_methods.py`",
        "",
        "## 主要指標",
        "",
        "| 方式 | N(全行) | N(採点対象) | Accuracy | ECE | Brier | AUROC |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        m = metrics[r.key].calibration
        auroc = "N/A" if m.auroc is None else f"{m.auroc:.3f}"
        lines.append(
            f"| {r.label} | {r.n_rows} | {r.n_scored} | "
            f"{r.n_correct_all}/{r.n_rows} = {r.n_correct_all / r.n_rows:.1%} | "
            f"{m.ece:.4f} | {m.brier:.4f} | {auroc} |"
        )
    lines += [
        "",
        "Accuracy は全行を分母にした値。確信度が取得できなかった行も誤答扱いせず"
        "分子から外すのではなく、正誤判定の結果をそのまま数えている。"
        "ECE / Brier / AUROC は確信度が取得できた行のみで計算している"
        "（分母は「N(採点対象)」列）。",
        "",
        "## Murphy 分解（BS = REL − RES + UNC）",
        "",
        "| 方式 | REL（低いほど良い） | RES（高いほど良い） | UNC |",
        "|---|---|---|---|",
    ]
    for r in results:
        mu = metrics[r.key].murphy
        lines.append(f"| {r.label} | {mu.rel:.4f} | {mu.res:.4f} | {mu.unc:.4f} |")
    lines += [
        "",
        "## 平均確信度と平均正答率",
        "",
        "| 方式 | 平均確信度 | 平均正答率 | 差（＋は自信過剰） |",
        "|---|---|---|---|",
    ]
    for r in results:
        m = metrics[r.key].calibration
        gap = m.mean_confidence - m.mean_accuracy
        lines.append(
            f"| {r.label} | {m.mean_confidence:.3f} | {m.mean_accuracy:.3f} | {gap:+.3f} |"
        )
    lines += ["", "## 図", "",
              "- `figures/fig1_reliability.png` 信頼度ダイアグラム",
              "- `figures/fig2_confidence.png` 確信度の分布",
              "- `figures/fig3_metrics.png` 指標比較", ""]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  保存: {out}")


def main() -> int:
    p = argparse.ArgumentParser(description="3方式の比較図と結果表を生成する")
    p.add_argument("--verb1s", default="results/mgsm_verb1s.csv")
    p.add_argument("--verb2s", default="results/mgsm_verb2s.csv")
    p.add_argument("--ling1s", default="results/mgsm_ling1s_rescored.csv")
    p.add_argument("--figdir", default="figures")
    p.add_argument("--out", default="results/comparison.md")
    args = p.parse_args()

    paths = {"verb_1s": args.verb1s, "verb_2s": args.verb2s, "ling_1s": args.ling1s}
    results: list[MethodResult] = []
    for key, label, color, marker in SERIES:
        path = Path(paths[key])
        if not path.exists():
            print(f"ERROR: ファイルがありません: {path}", file=sys.stderr)
            return 1
        r = load(path, key, label, color, marker)
        print(f"読み込み: {path} → {r.n_scored}/{r.n_rows} 行に確信度あり")
        if r.n_scored < r.n_rows:
            print(f"  [注意] {r.n_rows - r.n_scored} 行は指標計算から除外されます。")
        results.append(r)

    metrics = {r.key: compute_full(r.conf, r.correct, n_bins=N_BINS) for r in results}

    figdir = Path(args.figdir)
    try:
        fig_reliability(results, figdir / "fig1_reliability.png")
        fig_confidence(results, figdir / "fig2_confidence.png")
        fig_metrics(results, metrics, figdir / "fig3_metrics.png")
    except ImportError:
        print("ERROR: matplotlib が必要です。pip install matplotlib", file=sys.stderr)
        return 1

    write_markdown(results, metrics, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
