"""
LLMの応答から「回答」と「信頼度」をパースするユーティリティ

複数のモデルが微妙に異なるフォーマットで返してくることがあるので、
正規表現のバリエーションで頑健にパースする。
"""

import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    answer: str | None
    confidence: float | None  # 0.0〜1.0 に正規化済み
    raw_response: str
    parse_success: bool
    error: str | None = None


# 「回答: ...」を抽出する正規表現
ANSWER_PATTERNS = [
    r"回答\s*[::]\s*(.+?)(?=\n|$|信頼度|自信度|Confidence)",
    r"Answer\s*[::]\s*(.+?)(?=\n|$|Confidence)",
    r"答え\s*[::]\s*(.+?)(?=\n|$|信頼度|自信度)",
]

# 「信頼度: 75」や「信頼度: 75%」を抽出する正規表現
CONFIDENCE_PATTERNS_NUMERIC = [
    r"信頼度\s*[::]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
    r"Confidence\s*[::]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
    r"自信度\s*[::]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
]

# 「まったく自信がない」などの自然言語表現を数値化するマップ
VERBAL_TO_NUMERIC = {
    "まったく自信がない": 0.05,
    "全く自信がない": 0.05,
    "まったく自信なし": 0.05,
    "あまり自信がない": 0.25,
    "あまり自信なし": 0.25,
    "自信がない": 0.2,
    "どちらとも言えない": 0.5,
    "中程度": 0.5,
    "まあまあ自信がある": 0.7,
    "まあまあ自信あり": 0.7,
    "非常に自信がある": 0.95,
    "非常に自信あり": 0.95,
    "自信がある": 0.75,
    "絶対": 0.99,
    "確実": 0.98,
}


def parse_response(text: str, mode: str = "numeric_0_100") -> ParseResult:
    """
    モデルの応答をパースする。

    mode:
      - "numeric_0_100": 信頼度を0〜100の整数で期待
      - "numeric_1_5": 信頼度を1〜5の5段階で期待
      - "verbal": 信頼度を自然言語で期待
    """
    answer = _extract_first(text, ANSWER_PATTERNS)

    if mode in ("numeric_0_100", "numeric_1_5"):
        conf_raw = _extract_first(text, CONFIDENCE_PATTERNS_NUMERIC)
        if conf_raw is None:
            return ParseResult(
                answer=answer,
                confidence=None,
                raw_response=text,
                parse_success=False,
                error="confidence_not_found",
            )
        try:
            val = float(conf_raw)
            if mode == "numeric_0_100":
                confidence = val / 100.0
            else:  # numeric_1_5
                confidence = (val - 1) / 4.0
            confidence = max(0.0, min(1.0, confidence))
        except ValueError:
            return ParseResult(
                answer=answer,
                confidence=None,
                raw_response=text,
                parse_success=False,
                error="confidence_parse_fail",
            )
    elif mode == "verbal":
        confidence = _parse_verbal_confidence(text)
        if confidence is None:
            return ParseResult(
                answer=answer,
                confidence=None,
                raw_response=text,
                parse_success=False,
                error="verbal_confidence_unmatched",
            )
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return ParseResult(
        answer=answer,
        confidence=confidence,
        raw_response=text,
        parse_success=answer is not None,
    )


def _extract_first(text: str, patterns: list[str]) -> str | None:
    for pat in patterns:
        m = re.search(pat, text, re.MULTILINE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def _parse_verbal_confidence(text: str) -> float | None:
    for phrase, val in VERBAL_TO_NUMERIC.items():
        if phrase in text:
            return val
    return None


def judge_correctness(
    predicted: str, gold: str, answer_type: str
) -> bool:
    """
    回答が正解かどうかを判定。
    answer_type: "mc"(多肢選択) / "numeric" / "text"
    """
    if predicted is None:
        return False
    pred = predicted.strip()
    gold = gold.strip()

    if answer_type == "numeric":
        try:
            return abs(float(pred.replace(",", "")) - float(gold)) < 1e-6
        except ValueError:
            # 数値として読めない場合は文字列として比較
            return gold in pred
    elif answer_type == "mc":
        # 多肢選択: 選択肢本体が含まれていればOK
        return gold in pred
    elif answer_type == "text":
        # テキスト: 完全一致 or 含有
        return gold in pred or pred in gold
    return False


if __name__ == "__main__":
    # テスト
    sample_response = """回答: 包丁
信頼度: 95"""
    result = parse_response(sample_response)
    print(result)
    print("correct?", judge_correctness(result.answer, "包丁", "mc"))
