"""
実験結果 CSV から calibration サマリを自動生成する。

入力: run_pilot.py or mock_run.py が出力した CSV
       （列: id, domain, model, question, gold, answer, confidence, correct, parse_success）

出力: 以下を標準出力とファイル（results/summary.md）に出す
  1. 全体のサマリ（n, parse success, accuracy, ECE, Brier, AUROC）
  2. モデル別のサマリ
  3. ドメイン別のサマリ
  4. モデル × ドメイン のクロス集計（ECE を中心に）

使い方:
  $ python summarize_results.py --input results/mock_run.csv
  $ python summarize_results.py --input results/run_*.csv --glob
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from calibration import compute_all


def load_rows(paths: list[str]) -> list[dict]:
    """複数の CSV を読み込んで 1 つのリストにまとめる"""
    rows: list[dict] = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    return rows


def row_arrays(rows: list[dict]) -> tuple[np.ndarray, np.ndarray] | None:
    """confidence と correct を np.ndarray に変換。パース失敗行は除外。"""
    confs = []
    corrs = []
    for r in rows:
        if r.get("confidence", "") == "":
            continue
        try:
            conf = float(r["confidence"])
        except ValueError:
            continue
        if not (0.0 <= conf <= 1.0):
            # 0-100 表記が残っている場合は 0-1 に正規化
            conf = conf / 100.0 if conf <= 100.0 else 1.0
        confs.append(conf)
        corrs.append(int(r["correct"]))
    if not confs:
        return None
    return np.array(confs), np.array(corrs)


def fmt_metrics(label: str, rows: list[dict]) -> str:
    """1グループぶんのメトリクス行（Markdown表用）を返す"""
    arr = row_arrays(rows)
    n_rows = len(rows)
    n_parse = sum(int(r.get("parse_success", "0") or 0) for r in rows)
    parse_rate = n_parse / n_rows if n_rows > 0 else 0.0
    if arr is None:
        return f"| {label} | {n_rows} | {parse_rate:.1%} | N/A | N/A | N/A | N/A |"
    confs, corrs = arr
    m = compute_all(confs, corrs)
    auroc_str = f"{m.auroc:.3f}" if m.auroc is not None else "N/A"
    return (
        f"| {label} | {n_rows} | {parse_rate:.1%} | "
        f"{m.mean_accuracy:.1%} | {m.ece:.3f} | {m.brier:.3f} | {auroc_str} |"
    )


def summarize(rows: list[dict]) -> str:
    """Markdown 形式のサマリレポートを文字列として返す"""
    lines: list[str] = []
    lines.append("# 実験結果サマリ")
    lines.append("")
    lines.append(f"- **総データ点数**: {len(rows)}")
    lines.append(f"- **集計スクリプト**: `summarize_results.py`")
    lines.append("")

    # 全体
    lines.append("## 1. 全体")
    lines.append("")
    lines.append("| グループ | N | Parse成功率 | Accuracy | ECE | Brier | AUROC |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(fmt_metrics("全体", rows))
    lines.append("")

    # モデル別
    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_model[r.get("model", "unknown")].append(r)

    lines.append("## 2. モデル別")
    lines.append("")
    lines.append("| モデル | N | Parse成功率 | Accuracy | ECE | Brier | AUROC |")
    lines.append("|---|---|---|---|---|---|---|")
    for model in sorted(by_model):
        lines.append(fmt_metrics(model, by_model[model]))
    lines.append("")

    # ドメイン別
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_domain[r.get("domain", "unknown")].append(r)

    lines.append("## 3. ドメイン別")
    lines.append("")
    lines.append("| ドメイン | N | Parse成功率 | Accuracy | ECE | Brier | AUROC |")
    lines.append("|---|---|---|---|---|---|---|")
    for dom in sorted(by_domain):
        lines.append(fmt_metrics(dom, by_domain[dom]))
    lines.append("")

    # モデル × ドメインのクロス集計（ECE）
    lines.append("## 4. モデル × ドメイン のクロス集計（ECE）")
    lines.append("")
    models = sorted(by_model.keys())
    domains = sorted(by_domain.keys())
    header = "| モデル \\ ドメイン | " + " | ".join(domains) + " |"
    sep = "|" + "---|" * (len(domains) + 1)
    lines.append(header)
    lines.append(sep)
    for model in models:
        cells = [model]
        for dom in domains:
            subset = [r for r in rows
                      if r.get("model") == model and r.get("domain") == dom]
            arr = row_arrays(subset)
            if arr is None:
                cells.append("N/A")
            else:
                confs, corrs = arr
                m = compute_all(confs, corrs)
                cells.append(f"{m.ece:.3f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # 備考
    lines.append("## 5. 備考")
    lines.append("")
    lines.append("- ECE は 10-bin で計算")
    lines.append("- confidence は 0〜1 に正規化された値を使用")
    lines.append("- パース失敗行は calibration 指標の計算から除外")
    lines.append("- AUROC は全問正答 or 全問誤答のグループでは N/A")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True,
                    help="入力 CSV ファイル（複数可）")
    ap.add_argument("--glob", action="store_true",
                    help="入力をglobパターンとして展開")
    ap.add_argument("--output", default="results/summary.md",
                    help="Markdown 出力先")
    args = ap.parse_args()

    if args.glob:
        paths: list[str] = []
        for pattern in args.input:
            paths.extend(glob.glob(pattern))
    else:
        paths = args.input

    if not paths:
        print("エラー: 入力ファイルが見つかりません", file=sys.stderr)
        sys.exit(1)

    print(f"入力ファイル: {paths}")
    rows = load_rows(paths)
    print(f"読み込み行数: {len(rows)}")

    summary = summarize(rows)
    print()
    print(summary)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"\nサマリを {args.output} に保存しました")


if __name__ == "__main__":
    main()
