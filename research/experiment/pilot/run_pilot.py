"""
パイロット実験のメイン実行スクリプト

使い方:
  $ python run_pilot.py --model gpt-4o --questions questions_sample.csv --output results/gpt4o_raw.csv

環境変数:
  OPENAI_API_KEY: OpenAI API キー
  ANTHROPIC_API_KEY: Anthropic API キー
  GOOGLE_API_KEY: Google Gemini API キー

注意: 本スクリプトは雛形です。実際にAPIを叩く前に必ず指導教員に相談し、
使用量を小さく（最初は5問など）して動作確認してください。
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path

# このディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from prompts import BASIC_PROMPT_JA, build_prompt
from parser import parse_response, judge_correctness


def call_openai(model: str, prompt: str) -> str:
    """OpenAI API を呼び出す"""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("pip install openai が必要です")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content or ""


def call_anthropic(model: str, prompt: str) -> str:
    """Anthropic API を呼び出す"""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("pip install anthropic が必要です")
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model=model,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in response.content if hasattr(block, "text")
    )


def dispatch_call(model: str, prompt: str) -> str:
    """モデル名からAPIを振り分ける"""
    if model.startswith("gpt-") or model.startswith("o"):
        return call_openai(model, prompt)
    elif model.startswith("claude-"):
        return call_anthropic(model, prompt)
    else:
        raise ValueError(f"Unknown model: {model}")


def load_questions(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run(model: str, questions: list[dict], output: str, limit: int | None = None):
    """パイロット実験を実行する"""
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    rows = []

    target = questions[:limit] if limit else questions

    for i, q in enumerate(target, 1):
        prompt = build_prompt(
            BASIC_PROMPT_JA,
            q["question"],
            q.get("choices", ""),
        )
        print(f"[{i}/{len(target)}] {q['id']} ({q['domain']}): ", end="", flush=True)

        try:
            response = dispatch_call(model, prompt)
            parsed = parse_response(response)
            correct = judge_correctness(
                parsed.answer, q["correct_answer"], q["answer_type"]
            )
            print(
                f"answer={parsed.answer!r}, conf={parsed.confidence}, "
                f"correct={correct}"
            )
            rows.append({
                "id": q["id"],
                "domain": q["domain"],
                "model": model,
                "question": q["question"],
                "gold": q["correct_answer"],
                "answer": parsed.answer or "",
                "confidence": parsed.confidence if parsed.confidence is not None else "",
                "correct": int(correct),
                "parse_success": int(parsed.parse_success),
                "raw_response": parsed.raw_response.replace("\n", "\\n"),
            })
        except Exception as e:
            print(f"ERROR: {e}")
            rows.append({
                "id": q["id"],
                "domain": q["domain"],
                "model": model,
                "question": q["question"],
                "gold": q["correct_answer"],
                "answer": "",
                "confidence": "",
                "correct": 0,
                "parse_success": 0,
                "raw_response": f"ERROR: {e}",
            })

        # レート制限対策
        time.sleep(0.5)

    # CSV出力
    fieldnames = [
        "id", "domain", "model", "question", "gold",
        "answer", "confidence", "correct", "parse_success", "raw_response",
    ]
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. {len(rows)} rows written to {output}")

    # 簡易サマリー
    n_correct = sum(r["correct"] for r in rows)
    n_parse = sum(r["parse_success"] for r in rows)
    print(f"Accuracy: {n_correct}/{len(rows)} = {n_correct / len(rows):.2%}")
    print(f"Parse success rate: {n_parse}/{len(rows)} = {n_parse / len(rows):.2%}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="モデル名 (例: gpt-4o, claude-sonnet-4-6)")
    parser.add_argument("--questions", default="questions_sample.csv", help="問題CSVのパス")
    parser.add_argument("--output", required=True, help="結果CSVの出力先")
    parser.add_argument("--limit", type=int, default=None, help="最初のN問だけ実行する")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    run(args.model, questions, args.output, limit=args.limit)


if __name__ == "__main__":
    main()
