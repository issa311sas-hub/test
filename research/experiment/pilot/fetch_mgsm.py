"""
MGSM 日本語版（250問）を取得し、パイロット実験の CSV 形式に変換する。

データ出典:
  Shi et al. (2023) "Language Models are Multilingual Chain-of-Thought Reasoners" (ICLR)
  https://github.com/google-research/url-nlp/tree/main/mgsm
  MGSM は GSM8K (Cobbe et al. 2021) の 250 問を 10 言語へ人手翻訳したもの。

HuggingFace (`datasets`) 経由ではなく GitHub の原本 TSV を直接読む。
理由: 追加の依存や認証が不要で、ネットワーク制限下でも通りやすいため。

出力: questions_mgsm_ja.csv
  id,domain,question,choices,correct_answer,answer_type
  - domain = "math"（自由回答なので choices は空）
  - answer_type = "numeric"

使い方:
  python fetch_mgsm.py                      # questions_mgsm_ja.csv を生成
  python fetch_mgsm.py --limit 50           # 先頭50問だけ（お試し用）
  python fetch_mgsm.py --out mydata.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
import urllib.request
from pathlib import Path

MGSM_JA_URL = (
    "https://raw.githubusercontent.com/google-research/url-nlp/main/mgsm/mgsm_ja.tsv"
)

HEADER = ["id", "domain", "question", "choices", "correct_answer", "answer_type"]


def download(url: str) -> str:
    print(f"取得中: {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:
        # file:// で開いた場合 status は None になるので、その場合は素通しする
        if resp.status is not None and resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status} が返りました: {url}")
        return resp.read().decode("utf-8")


def parse_tsv(text: str) -> list[tuple[str, str]]:
    """MGSM の TSV は「問題文 \t 答え（数値）」の2列・ヘッダ無し。"""
    rows: list[tuple[str, str]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            print(f"  [警告] {lineno} 行目は 2 列でないため飛ばします（{len(parts)} 列）")
            continue
        question, answer = parts[0].strip(), parts[1].strip()
        if not question or not answer:
            print(f"  [警告] {lineno} 行目は空欄を含むため飛ばします")
            continue
        rows.append((question, answer))
    return rows


def validate(rows: list[tuple[str, str]]) -> None:
    """数値回答として読めない行があれば、静かに通さず知らせる。"""
    bad = []
    for i, (_, ans) in enumerate(rows, start=1):
        try:
            float(ans.replace(",", ""))
        except ValueError:
            bad.append((i, ans))
    if bad:
        print(f"  [警告] 数値として読めない答えが {len(bad)} 件あります: {bad[:5]}")
        print("         parser.judge_correctness は numeric 判定なので確認してください。")
    else:
        print(f"  検証OK: 全 {len(rows)} 問の答えが数値として読めます")


def write_csv(rows: list[tuple[str, str]], out: Path) -> None:
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for i, (question, answer) in enumerate(rows, start=1):
            w.writerow([f"mgsm_ja_{i:03d}", "math", question, "", answer, "numeric"])
    print(f"書き出し完了: {out} ({len(rows)} 問)")


def main() -> int:
    p = argparse.ArgumentParser(description="MGSM 日本語版をパイロット用 CSV に変換")
    p.add_argument("--url", default=MGSM_JA_URL, help="取得元 TSV の URL")
    p.add_argument("--limit", type=int, default=None, help="先頭 N 問だけ出力")
    p.add_argument(
        "--out",
        default=str(Path(__file__).parent / "questions_mgsm_ja.csv"),
        help="出力 CSV パス",
    )
    args = p.parse_args()

    try:
        text = download(args.url)
    except Exception as e:
        print(f"ERROR: データ取得に失敗しました: {e}", file=sys.stderr)
        print(
            "ネットワーク制限がある場合は、ブラウザで下記を開いて手元に保存し、\n"
            f"  {args.url}\n"
            "--url file:///保存先/mgsm_ja.tsv のように指定してください。",
            file=sys.stderr,
        )
        return 1

    rows = parse_tsv(text)
    if not rows:
        print("ERROR: 1 問も読み取れませんでした。TSV の形式を確認してください。", file=sys.stderr)
        return 1
    print(f"読み取り: {len(rows)} 問")
    validate(rows)

    if args.limit is not None:
        if args.limit < 1:
            print("ERROR: --limit は 1 以上を指定してください。", file=sys.stderr)
            return 1
        rows = rows[: args.limit]
        print(f"--limit により {len(rows)} 問に絞り込みました")

    write_csv(rows, Path(args.out))
    print("\n先頭 1 問のプレビュー:")
    print(f"  問題: {rows[0][0][:60]}...")
    print(f"  答え: {rows[0][1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
