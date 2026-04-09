"""
モック実行: API呼び出しなしで run_pilot.py 相当の処理を通す

目的:
- API keyがない環境での動作確認
- パース・集計ロジックの統合テスト
- 後続のpandasによる集計処理の検証

使い方:
  $ python mock_run.py
"""

import csv
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parser import parse_response, judge_correctness
from prompts import BASIC_PROMPT_JA, build_prompt


def mock_llm_response(question: str, gold: str, answer_type: str) -> str:
    """
    モックLLM応答: 70%の確率で正解を返し、ランダムな信頼度を返す。
    calibration が適当な値になるように、正解時は高信頼度、
    不正解時は中信頼度を返すようにする。
    """
    is_correct = random.random() < 0.7
    if is_correct:
        answer = gold
        confidence = random.randint(70, 100)
    else:
        # 不正解をランダムに生成
        if answer_type == "numeric":
            answer = str(random.randint(1, 1000))
        else:
            answer = "不明"
        confidence = random.randint(30, 80)
    return f"回答: {answer}\n信頼度: {confidence}"


def run_mock(questions_path: str, output: str, limit: int | None = None):
    random.seed(42)

    with open(questions_path, encoding="utf-8") as f:
        questions = list(csv.DictReader(f))

    if limit:
        questions = questions[:limit]

    rows = []
    for i, q in enumerate(questions, 1):
        prompt = build_prompt(BASIC_PROMPT_JA, q["question"], q.get("choices", ""))
        response = mock_llm_response(q["question"], q["correct_answer"], q["answer_type"])
        parsed = parse_response(response)
        correct = judge_correctness(parsed.answer, q["correct_answer"], q["answer_type"])

        rows.append({
            "id": q["id"],
            "domain": q["domain"],
            "model": "mock",
            "question": q["question"],
            "gold": q["correct_answer"],
            "answer": parsed.answer or "",
            "confidence": parsed.confidence if parsed.confidence is not None else "",
            "correct": int(correct),
            "parse_success": int(parsed.parse_success),
        })
        print(f"[{i}/{len(questions)}] {q['id']} ({q['domain']}): "
              f"answer={parsed.answer!r}, conf={parsed.confidence}, correct={correct}")

    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "id", "domain", "model", "question", "gold",
            "answer", "confidence", "correct", "parse_success",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    n_correct = sum(r["correct"] for r in rows)
    n_parse = sum(r["parse_success"] for r in rows)
    print(f"\nDone. {len(rows)} rows written to {output}")
    print(f"Accuracy: {n_correct}/{len(rows)} = {n_correct / len(rows):.2%}")
    print(f"Parse success: {n_parse}/{len(rows)} = {n_parse / len(rows):.2%}")

    # Calibration metrics の集計
    try:
        import numpy as np
        from calibration import compute_all
        confs = np.array([float(r["confidence"]) for r in rows if r["confidence"] != ""])
        corrs = np.array([r["correct"] for r in rows if r["confidence"] != ""])
        metrics = compute_all(confs, corrs)
        print(f"\nCalibration metrics (mock data):")
        print(f"  ECE: {metrics.ece:.4f}")
        print(f"  Brier: {metrics.brier:.4f}")
        print(f"  AUROC: {metrics.auroc:.4f}" if metrics.auroc else "  AUROC: N/A")
    except ImportError:
        print("\n(numpy 未導入のため calibration metrics はスキップ)")

    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--questions", default="questions_sample.csv")
    p.add_argument("--output", default="results/mock_run.csv")
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    run_mock(args.questions, args.output, args.limit)
