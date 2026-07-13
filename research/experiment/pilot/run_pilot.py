"""
パイロット実験のメイン実行スクリプト（v2: 3方式対応 + Murphy 分解）

使い方:
  # Verb.1S で Claude を 5 問だけ試す
  $ python run_pilot.py --model claude-sonnet-4-6 --method verb_1s \\
      --questions questions_sample.csv --output results/test.csv --limit 5

  # Verb.2S で GPT-4o を全問実行
  $ python run_pilot.py --model gpt-4o --method verb_2s \\
      --questions questions_sample.csv --output results/gpt4o_verb2s.csv

環境変数:
  OPENAI_API_KEY     : OpenAI API キー
  ANTHROPIC_API_KEY  : Anthropic API キー
  GOOGLE_API_KEY     : Google Gemini API キー

注意: 最初は --limit 5 で動作確認してから本番実行してください。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from prompts import build_prompt, LING_TO_NUM, PROMPT_METHODS
from parser import parse_response, judge_correctness


# ---------------------------------------------------------------------------
# API 呼び出し
# ---------------------------------------------------------------------------

MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 2.0


def _with_retry(fn, *args, **kwargs):
    """レート制限・一時的なAPIエラーに対する exponential backoff 付き再試行"""
    for attempt in range(MAX_RETRIES):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = BASE_BACKOFF_SECONDS * (2 ** attempt)
            print(f"  retrying after error ({e}); wait {wait:.1f}s [{attempt+1}/{MAX_RETRIES}]")
            time.sleep(wait)


def call_openai(model: str, messages: list[dict]) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("pip install openai が必要です")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0.0)
    return resp.choices[0].message.content or ""


def call_anthropic(model: str, messages: list[dict]) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("pip install anthropic が必要です")
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model, max_tokens=512, temperature=0.0,
        messages=messages,
    )
    return "".join(b.text for b in resp.content if hasattr(b, "text"))


def call_gemini(model: str, messages: list[dict]) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise RuntimeError("pip install google-generativeai が必要です")
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    m = genai.GenerativeModel(model)
    # Gemini は単純な最後の user メッセージを使用
    text = messages[-1]["content"]
    resp = m.generate_content(text, generation_config={"temperature": 0.0})
    return resp.text or ""


def dispatch(model: str, messages: list[dict]) -> str:
    """モデル名から API を振り分ける（レート制限時は自動的に再試行する）"""
    if model.startswith("gpt-") or model.startswith("o"):
        return _with_retry(call_openai, model, messages)
    elif model.startswith("claude-"):
        return _with_retry(call_anthropic, model, messages)
    elif model.startswith("gemini"):
        return _with_retry(call_gemini, model, messages)
    else:
        raise ValueError(f"Unknown model prefix: {model!r}")


# ---------------------------------------------------------------------------
# 確信度の正規化（0.0〜1.0 に統一）
# ---------------------------------------------------------------------------

def normalize_confidence(raw: str | float | None, method: str) -> float | None:
    """
    各方式の出力を 0.0〜1.0 の float に変換する。
    変換不能な場合は None を返す。
    """
    if raw is None:
        return None
    if method == "ling_1s":
        # 文字列 → 数値マッピング
        if isinstance(raw, str):
            return LING_TO_NUM.get(raw.strip())
        return None
    # verb_1s / verb_2s: float に変換して範囲チェック
    try:
        v = float(str(raw).replace("%", "").strip())
    except ValueError:
        return None
    if v > 1.0:
        v = v / 100.0  # 0〜100 スケールで返した場合を救済
    return float(max(0.0, min(1.0, v)))


# ---------------------------------------------------------------------------
# 1 問の実行
# ---------------------------------------------------------------------------

def run_one(
    model: str, method: str, q: dict, verbose: bool = True
) -> dict:
    """1 問を実行して結果 dict を返す。例外は raw_response に記録する。"""
    domain = q.get("domain", "math")
    question = q["question"]
    choices = q.get("choices", "")

    try:
        if method == "verb_1s" or method == "ling_1s":
            prompt = build_prompt(method, domain, question, choices=choices)
            assert isinstance(prompt, str)
            messages = [{"role": "user", "content": prompt}]
            raw = dispatch(model, messages)
            parsed = parse_response(raw)
            conf_raw = parsed.confidence
            turn1_raw = ""

        elif method == "verb_2s":
            t1, t2 = build_prompt("verb_2s", domain, question, choices=choices)
            messages = [{"role": "user", "content": t1}]
            raw_t1 = dispatch(model, messages)
            parsed_t1 = parse_response(raw_t1)
            turn1_raw = parsed_t1.answer or ""
            # Turn2: セッション継続
            messages += [
                {"role": "assistant", "content": raw_t1},
                {"role": "user", "content": t2.replace("（未取得）", turn1_raw)},
            ]
            raw = dispatch(model, messages)
            parsed = parse_response(raw)
            # Turn2 の確信度を採用、回答は Turn1 から
            conf_raw = parsed.confidence
            parsed.answer = parsed_t1.answer

        else:
            raise ValueError(f"Unknown method: {method!r}")

        conf = normalize_confidence(conf_raw, method)
        correct = judge_correctness(parsed.answer, q["correct_answer"], q["answer_type"])

        if verbose:
            print(
                f"  answer={parsed.answer!r}  conf={conf}  correct={correct}  "
                f"parse_ok={parsed.parse_success}"
            )

        return {
            "id": q["id"],
            "domain": domain,
            "model": model,
            "method": method,
            "question": q["question"],
            "gold": q["correct_answer"],
            "answer": parsed.answer or "",
            "confidence_raw": str(conf_raw) if conf_raw is not None else "",
            "confidence": conf if conf is not None else "",
            "correct": int(correct),
            "parse_success": int(parsed.parse_success),
            "raw_response": raw.replace("\n", "\\n"),
        }

    except Exception as e:
        if verbose:
            print(f"  ERROR: {e}")
        return {
            "id": q["id"],
            "domain": domain,
            "model": model,
            "method": method,
            "question": q["question"],
            "gold": q["correct_answer"],
            "answer": "",
            "confidence_raw": "",
            "confidence": "",
            "correct": 0,
            "parse_success": 0,
            "raw_response": f"ERROR: {e}",
        }


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "id", "domain", "model", "method", "question", "gold",
    "answer", "confidence_raw", "confidence", "correct", "parse_success", "raw_response",
]


def run(model: str, method: str, questions: list[dict], output: str, limit: int | None = None):
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    target = questions[:limit] if limit else questions
    rows = []

    for i, q in enumerate(target, 1):
        print(f"[{i}/{len(target)}] {q['id']} ({q.get('domain', '?')}): ", end="", flush=True)
        row = run_one(model, method, q)
        rows.append(row)
        time.sleep(0.5)

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    # サマリー
    n_correct = sum(int(r["correct"]) for r in rows)
    n_parse = sum(int(r["parse_success"]) for r in rows)
    valid_confs = [float(r["confidence"]) for r in rows if r["confidence"] != ""]

    print(f"\n{'='*50}")
    print(f"Model={model}  Method={method}  N={len(rows)}")
    print(f"Accuracy:      {n_correct}/{len(rows)} = {n_correct/len(rows):.2%}")
    print(f"Parse success: {n_parse}/{len(rows)} = {n_parse/len(rows):.2%}")
    if valid_confs:
        import numpy as np
        from calibration import compute_full
        confs = np.array(valid_confs)
        correct_arr = np.array([int(r["correct"]) for r in rows if r["confidence"] != ""])
        fm = compute_full(confs, correct_arr)
        c = fm.calibration
        m = fm.murphy
        print(f"ECE:   {c.ece:.4f}")
        print(f"Brier: {c.brier:.4f}")
        print(f"AUROC: {c.auroc:.4f}" if c.auroc is not None else "AUROC: N/A")
        print(f"--- Murphy decomposition ---")
        print(f"REL:   {m.rel:.4f}  (↓ 低いほど較正が良い)")
        print(f"RES:   {m.res:.4f}  (↑ 高いほど識別能力が高い)")
        print(f"UNC:   {m.unc:.4f}  (データ固有の定数)")

        # JSON サマリーも保存
        summary_path = output.replace(".csv", "_summary.json")
        summary = {
            "model": model, "method": method, "n": len(rows),
            "accuracy": round(n_correct / len(rows), 4),
            "parse_rate": round(n_parse / len(rows), 4),
            "ece": round(c.ece, 4),
            "brier": round(c.brier, 4),
            "auroc": round(c.auroc, 4) if c.auroc else None,
            "murphy": {"rel": round(m.rel, 4), "res": round(m.res, 4), "unc": round(m.unc, 4)},
        }
        with open(summary_path, "w", encoding="utf-8") as jf:
            json.dump(summary, jf, ensure_ascii=False, indent=2)
        print(f"\nSummary saved: {summary_path}")

    print(f"Results saved: {output}")


def load_questions(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description="パイロット実験実行スクリプト v2")
    parser.add_argument("--model", required=True,
                        help="モデル名 (例: gpt-4o, claude-sonnet-4-6, gemini-2.0-flash)")
    parser.add_argument("--method", required=True, choices=list(PROMPT_METHODS),
                        help="確信度引き出し方式 (verb_1s / verb_2s / ling_1s)")
    parser.add_argument("--questions", default="questions_sample.csv",
                        help="問題 CSV のパス")
    parser.add_argument("--output", required=True,
                        help="結果 CSV の出力先")
    parser.add_argument("--limit", type=int, default=None,
                        help="最初の N 問だけ実行する（動作確認用）")
    args = parser.parse_args()

    questions = load_questions(args.questions)
    run(args.model, args.method, questions, args.output, limit=args.limit)


if __name__ == "__main__":
    main()
