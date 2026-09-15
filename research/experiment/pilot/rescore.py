"""
既存の結果 CSV を、API を再実行せずに再採点する。

run_pilot.py は各問の生の応答を raw_response 列に保存している。
パーサの不具合を直した場合、応答そのものは変わらないので、保存済みの
raw_response から confidence / correct / parse_success を計算し直せる。

想定用途:
  Ling.1S の確信度が言語表現のまま数値化されず confidence が空になっていた
  不具合（parse_response が数値モード固定だった）の後追い修正。

使い方:
  python rescore.py --input results/mgsm_ling1s.csv
      → results/mgsm_ling1s_rescored.csv を出力（元ファイルは書き換えない）

  python rescore.py --input results/mgsm_ling1s.csv --out results/fixed.csv

注意: Verb.2S の raw_response は Turn2（確信度のみ）の応答なので、回答は
再抽出できない。そのため Verb.2S では既存の answer 列をそのまま使う。
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parser import (
    CONFIDENCE_PATTERNS_TEXT,
    _extract_first,
    judge_correctness,
    parse_response,
)
from run_pilot import PARSE_MODES, normalize_confidence, FIELDNAMES


def unescape(raw: str) -> str:
    """run_pilot.py が保存時に改行を \\n に置換しているのを戻す。"""
    return raw.replace("\\n", "\n")


def rescore_row(row: dict, qmeta: dict[str, dict] | None) -> dict:
    method = row.get("method") or "verb_1s"
    raw = unescape(row.get("raw_response", ""))

    if not raw or raw.startswith("ERROR:"):
        # 実行時にエラーだった行は再採点しても復活しない
        return row

    mode = PARSE_MODES.get(method, "numeric_0_100")
    parsed = parse_response(raw, mode=mode)

    # Verb.2S は Turn2 の応答しか保存されておらず回答を再抽出できないため、
    # 既存の answer 列を正とする。
    answer = row.get("answer") or "" if method == "verb_2s" else (parsed.answer or "")

    conf = normalize_confidence(parsed.confidence, method)

    # 正誤判定には answer_type と choices が要る。結果 CSV には含まれない
    # ことがあるので、問題 CSV から引けた場合のみ再判定する。引けない場合に
    # 既定値（numeric）で判定すると、選択式の問題が軒並み不正解に書き換わる。
    meta = _lookup_meta(row, qmeta)
    if meta is None:
        correct = int(row.get("correct") or 0)
    else:
        correct = int(
            judge_correctness(
                answer or None,
                row["gold"],
                meta.get("answer_type") or "numeric",
                choices=meta.get("choices") or None,
            )
        )
    parse_ok = bool(answer) and conf is not None

    out = dict(row)
    out["answer"] = answer
    out["confidence_raw"] = _raw_confidence_text(raw, parsed.confidence, mode)
    out["confidence"] = conf if conf is not None else ""
    out["correct"] = correct
    out["parse_success"] = int(parse_ok)
    return out


def _lookup_meta(row: dict, qmeta: dict[str, dict] | None) -> dict | None:
    """その行の answer_type / choices を、結果CSV → 問題CSV の順で探す。"""
    if row.get("answer_type"):
        return {"answer_type": row["answer_type"], "choices": row.get("choices")}
    if qmeta is not None:
        return qmeta.get(row.get("id", ""))
    return None


def _raw_confidence_text(raw: str, conf: float | None, mode: str) -> str:
    """confidence_raw にはモデルが実際に書いた表現を残す。

    Ling.1S で数値に変換した値だけを残すと、再採点し直したときに
    モデルが何と言ったのか分からなくなる。
    """
    if mode == "ling":
        field = _extract_first(raw, CONFIDENCE_PATTERNS_TEXT)
        if field:
            return field
    return str(conf) if conf is not None else ""


def main() -> int:
    p = argparse.ArgumentParser(description="保存済み応答から結果を再採点する")
    p.add_argument("--input", required=True, help="再採点する結果 CSV")
    p.add_argument("--out", default=None, help="出力先（既定: <input>_rescored.csv）")
    p.add_argument(
        "--questions",
        default=None,
        help="問題CSV。answer_type / choices を id で引くのに使う。"
        "指定しない場合、正誤判定は再計算せず元の値を保持する。",
    )
    args = p.parse_args()

    qmeta = None
    if args.questions:
        qpath = Path(args.questions)
        if not qpath.exists():
            print(f"ERROR: 問題CSVがありません: {qpath}", file=sys.stderr)
            return 1
        with qpath.open(encoding="utf-8") as f:
            qmeta = {r["id"]: r for r in csv.DictReader(f)}
        print(f"問題CSV読み込み: {qpath} ({len(qmeta)} 問)")

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: ファイルがありません: {src}", file=sys.stderr)
        return 1
    dst = Path(args.out) if args.out else src.with_name(src.stem + "_rescored.csv")

    with src.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print(f"ERROR: {src} にデータ行がありません。", file=sys.stderr)
        return 1

    if "raw_response" not in rows[0]:
        print(
            f"ERROR: {src} に raw_response 列がありません。再採点できません。",
            file=sys.stderr,
        )
        return 1

    before_conf = sum(1 for r in rows if r.get("confidence") not in ("", None))
    rescored = [rescore_row(r, qmeta) for r in rows]
    after_conf = sum(1 for r in rescored if r.get("confidence") not in ("", None))
    after_correct = sum(int(r["correct"]) for r in rescored)

    fieldnames = [c for c in FIELDNAMES if c in rescored[0]]
    fieldnames += [c for c in rescored[0] if c not in fieldnames]
    with dst.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rescored)

    n = len(rows)
    print(f"再採点: {src} → {dst}")
    print(f"  行数: {n}")
    print(f"  確信度あり: {before_conf} → {after_conf}")
    print(f"  正答: {after_correct}/{n} = {after_correct / n:.2%}")
    if qmeta is None:
        print("  （--questions 未指定のため correct 列は元の値を保持しました）")
    if after_conf < n:
        print(f"  [注意] {n - after_conf} 行は確信度を取得できませんでした。")
        print("         raw_response 列を目視して応答形式を確認してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
