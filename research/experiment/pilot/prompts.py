"""
確信度引き出しプロンプトテンプレート (研究計画書 v0.3 確定版)

3 方式:
  VERB_1S  - Verbalized 1-Stage: 回答と確信度を同時出力 (Xiong 2024 Vanilla)
  VERB_2S  - Verbalized 2-Stage: Turn1で回答 → Turn2で確信度 (Tian 2023 Two-Stage)
  LING_1S  - Linguistic 1-Stage: 言語表現で確信度を表現 (Tian 2023 Linguistic)

数値マッピング (LING_1S):
  ほぼ確実         → 0.95
  かなり自信がある  → 0.80
  どちらともいえない → 0.50
  あまり自信がない  → 0.25
  ほとんどわからない → 0.05
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Verb.1S: 回答と確信度（0.0〜1.0）を同時出力
# ---------------------------------------------------------------------------
VERB_1S_MATH = """以下の数学の問題を読み、回答と、その回答が正しいと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]
確信度: [0.0〜1.0の数値]"""

VERB_1S_MC = """以下の問題を読み、選択肢の中から最も適切な答えを選び、その回答が正しいと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

問題: {question}
{choices_section}
以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/D のいずれか]
確信度: [0.0〜1.0の数値]"""

VERB_1S_TRANS = """以下の日本語を英語に翻訳し、その翻訳が正確だと思う確率（確信度）を答えてください。
確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。

日本語: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳]
確信度: [0.0〜1.0の数値]"""

# ---------------------------------------------------------------------------
# Verb.2S Turn1: 回答のみを取得
# ---------------------------------------------------------------------------
VERB_2S_TURN1_MATH = """以下の数学の問題に回答してください。

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]"""

VERB_2S_TURN1_MC = """以下の問題を読み、選択肢の中から最も適切な答えを選んでください。

問題: {question}
{choices_section}
以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/D のいずれか]"""

VERB_2S_TURN1_TRANS = """以下の日本語を英語に翻訳してください。

日本語: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳]"""

# ---------------------------------------------------------------------------
# Verb.2S Turn2: 確信度のみを質問
# ---------------------------------------------------------------------------
VERB_2S_TURN2 = """あなたは先ほどの問題に対して「{answer}」と回答しました。
この回答が正しい確率を0.0（まったく自信がない）から1.0（完全に確信している）の数値で答えてください。

以下の形式で回答してください。形式以外の出力はしないでください。
確信度: [0.0〜1.0の数値]"""

# ---------------------------------------------------------------------------
# Ling.1S: 言語表現で確信度を表現
# ---------------------------------------------------------------------------
LING_1S_MATH = """以下の数学の問題を読み、回答と、その回答に対する自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

・ほぼ確実
・かなり自信がある
・どちらともいえない
・あまり自信がない
・ほとんどわからない

問題: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
回答: [数値のみ]
確信度: [上記5つの表現から1つ]"""

LING_1S_MC = """以下の問題を読み、選択肢の中から最も適切な答えを選び、その自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

・ほぼ確実
・かなり自信がある
・どちらともいえない
・あまり自信がない
・ほとんどわからない

問題: {question}
{choices_section}
以下の形式で回答してください。形式以外の出力はしないでください。
回答: [A/B/C/D のいずれか]
確信度: [上記5つの表現から1つ]"""

LING_1S_TRANS = """以下の日本語を英語に翻訳し、その翻訳への自信の度合いを答えてください。
自信の度合いは以下の5つの表現から最も当てはまるものを1つ選んでください。

・ほぼ確実
・かなり自信がある
・どちらともいえない
・あまり自信がない
・ほとんどわからない

日本語: {question}

以下の形式で回答してください。形式以外の出力はしないでください。
翻訳: [英語翻訳]
確信度: [上記5つの表現から1つ]"""

# ---------------------------------------------------------------------------
# Linguistic confidence → numeric mapping
# ---------------------------------------------------------------------------
LING_TO_NUM: dict[str, float] = {
    "ほぼ確実": 0.95,
    "かなり自信がある": 0.80,
    "どちらともいえない": 0.50,
    "あまり自信がない": 0.25,
    "ほとんどわからない": 0.05,
}

# ---------------------------------------------------------------------------
# ドメイン × 方式でテンプレートを引く辞書
# ---------------------------------------------------------------------------
PROMPT_TEMPLATES: dict[str, dict[str, str]] = {
    "verb_1s": {
        "math": VERB_1S_MATH,
        "commonsense": VERB_1S_MC,
        "knowledge": VERB_1S_MC,
        "translation": VERB_1S_TRANS,
    },
    "verb_2s_turn1": {
        "math": VERB_2S_TURN1_MATH,
        "commonsense": VERB_2S_TURN1_MC,
        "knowledge": VERB_2S_TURN1_MC,
        "translation": VERB_2S_TURN1_TRANS,
    },
    "verb_2s_turn2": VERB_2S_TURN2,
    "ling_1s": {
        "math": LING_1S_MATH,
        "commonsense": LING_1S_MC,
        "knowledge": LING_1S_MC,
        "translation": LING_1S_TRANS,
    },
}

PROMPT_METHODS = ("verb_1s", "verb_2s", "ling_1s")


def build_prompt(
    method: str,
    domain: str,
    question: str,
    choices: str | None = None,
    turn1_answer: str | None = None,
) -> str | tuple[str, str]:
    """
    プロンプトを組み立てる。

    method: "verb_1s" | "verb_2s" | "ling_1s"
    domain: "math" | "commonsense" | "knowledge" | "translation"
    choices: 選択肢文字列 ("|" 区切り、MC タスクのみ)
    turn1_answer: Verb.2S のみ Turn2 の組み立てに使う

    Returns:
      verb_1s, ling_1s → str (1 プロンプト)
      verb_2s → tuple[str, str] (Turn1, Turn2)
    """
    choices_section = _build_choices_section(choices)

    if method == "verb_1s":
        tmpl = PROMPT_TEMPLATES["verb_1s"][domain]
        return tmpl.format(question=question, choices_section=choices_section)

    elif method == "verb_2s":
        t1_tmpl = PROMPT_TEMPLATES["verb_2s_turn1"][domain]
        t1 = t1_tmpl.format(question=question, choices_section=choices_section)
        t2 = PROMPT_TEMPLATES["verb_2s_turn2"].format(answer=turn1_answer or "（未取得）")
        return t1, t2

    elif method == "ling_1s":
        tmpl = PROMPT_TEMPLATES["ling_1s"][domain]
        return tmpl.format(question=question, choices_section=choices_section)

    else:
        raise ValueError(f"Unknown method: {method!r}. Choose from {PROMPT_METHODS}")


def _build_choices_section(choices: str | None) -> str:
    if not choices or not choices.strip():
        return ""
    items = [c.strip() for c in choices.split("|") if c.strip()]
    lines = "\n".join(f"  {chr(ord('A') + i)}. {c}" for i, c in enumerate(items))
    return f"\n選択肢:\n{lines}\n"


if __name__ == "__main__":
    print("=== Verb.1S (math) ===")
    print(build_prompt("verb_1s", "math", "12 × 7 = ?"))
    print("\n=== Verb.2S Turn1 (MC) ===")
    t1, t2 = build_prompt("verb_2s", "commonsense", "犬が好む食べ物は？", choices="骨|魚|草|砂")
    print(t1)
    print("--- Turn2 ---")
    print(t2)
    print("\n=== Ling.1S (translation) ===")
    print(build_prompt("ling_1s", "translation", "今日は天気がいい。"))
