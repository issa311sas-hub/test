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
    r"回答\s*[:：]\s*(.+?)(?=\n|$|確信度|信頼度|自信度|Confidence)",
    r"Answer\s*[:：]\s*(.+?)(?=\n|$|Confidence)",
    r"答え\s*[:：]\s*(.+?)(?=\n|$|確信度|信頼度|自信度)",
]

# 「確信度: 0.9」「信頼度: 75」「信頼度: 75%」等を抽出する正規表現。
# prompts.py のテンプレートは「確信度」を使うため、これを最初に置く。
CONFIDENCE_PATTERNS_NUMERIC = [
    r"確信度\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
    r"信頼度\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
    r"Confidence\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
    r"自信度\s*[:：]\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
]

# 「確信度: かなり自信がある」の値部分（テキスト）を取り出す正規表現。
# Ling.1S では確信度が数値ではなく言語表現で返るため、数値用とは別に持つ。
CONFIDENCE_PATTERNS_TEXT = [
    r"確信度\s*[:：]\s*(.+?)(?=\n|$)",
    r"信頼度\s*[:：]\s*(.+?)(?=\n|$)",
    r"自信の度合い\s*[:：]\s*(.+?)(?=\n|$)",
    r"Confidence\s*[:：]\s*(.+?)(?=\n|$)",
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
      - "ling": Ling.1S の5つの定型表現（prompts.LING_TO_NUM）を期待
      - "verbal": 信頼度を自然言語で期待（定型外の言い回しも拾う緩い判定）
    """
    answer = _extract_last(text, ANSWER_PATTERNS)

    if mode == "ling":
        confidence = _parse_ling_confidence(text)
        if confidence is None:
            return ParseResult(
                answer=answer,
                confidence=None,
                raw_response=text,
                parse_success=False,
                error="ling_confidence_unmatched",
            )
    elif mode in ("numeric_0_100", "numeric_1_5"):
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
                # prompts.py のテンプレートは 0.0〜1.0 を要求するが、モデルが
                # 0〜100 で返してくることもある。
                # 「%」が明記されている場合は百分率として必ず 100 で割る。
                # 値域だけで判断すると「0.5%」を 0.5（=50%）と誤って読む。
                # 「%」が無い場合にかぎり、値域から尺度を推定する。
                if _has_percent(text):
                    confidence = val / 100.0
                else:
                    confidence = val if val <= 1.0 else val / 100.0
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


# 確信度の値に百分率記号が付いているか
_CONF_PERCENT_RE = re.compile(
    r"(?:確信度|信頼度|自信度|Confidence)\s*[:：]\s*[0-9]+(?:\.[0-9]+)?\s*[%％]"
)


def _has_percent(text: str) -> bool:
    """確信度の値が百分率で書かれているか。"""
    return bool(_CONF_PERCENT_RE.search(text))


def _extract_last(text: str, patterns: list[str]) -> str | None:
    """応答中で最後に現れた回答を返す。

    モデルは「回答: [計算します]」のような仮の記入をしてから途中式を書き、
    最後に「回答: 64」と本来の答えを書くことがある。最初の一致を採ると
    仮の記入のほうを回答として扱ってしまうため、最後の一致を採る。

    パターンの優先順ではなく出現位置で選ぶ。パターンごとに順に探して最初に
    一致したものを採ると、「回答:」と「Answer:」のように見出しが混在する
    応答で、後ろにある本来の回答ではなく前にある見出しの側を拾ってしまう。
    """
    best: tuple[int, str] | None = None
    for pat in patterns:
        for m in re.finditer(pat, text, re.MULTILINE | re.DOTALL):
            if best is None or m.start() > best[0]:
                best = (m.start(), m.group(1).strip())
    return best[1] if best else None


def _extract_first(text: str, patterns: list[str]) -> str | None:
    for pat in patterns:
        m = re.search(pat, text, re.MULTILINE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def _parse_ling_confidence(text: str) -> float | None:
    """Ling.1S の定型5表現を数値に変換する。

    プロンプト側（prompts.LING_TO_NUM）と同一のマッピングを使うため、
    表現の追加・変更が片方だけに入ることがない。「確信度:」欄の値を優先し、
    欄が取れない場合のみ応答全体から探す。部分一致の取り違えを避けるため、
    長い表現から順に照合する。
    """
    from prompts import LING_TO_NUM  # prompts は parser を import しないので循環しない

    ordered = sorted(LING_TO_NUM.items(), key=lambda kv: -len(kv[0]))
    field = _extract_first(text, CONFIDENCE_PATTERNS_TEXT)
    for haystack in (field, text):
        if not haystack:
            continue
        for phrase, val in ordered:
            if phrase in haystack:
                return val
    return None


def _parse_verbal_confidence(text: str) -> float | None:
    for phrase, val in VERBAL_TO_NUMERIC.items():
        if phrase in text:
            return val
    return None


# 数値回答から取り除いてよい表記上の付加。
#
# ここに単位（円・個・cm 等）は含めない。正解欄に単位が無いことは、回答側の
# 単位を消してよい理由にならないためである。たとえば 100 ドルを問う設問で
# 「100セント」と答えた場合、単位を消すと gold=100 と一致してしまう。
# 単位の整合性を見るには設問が要求する単位を持つ必要があり、本研究の
# 採点規則はそこまで踏み込まない。
#
# 百分率記号のみ例外として扱う。MGSM 日本語版で確率を問う設問（mgsm_ja_227）
# の正解が単位なしの数値で与えられており、「33%」という回答は設問が要求する
# 単位を伴った同じ値だからである。この判断は設問を確認したうえでのもので、
# 一般の単位に拡張できるものではない。
_PERCENT_SUFFIXES = ("%", "％")
_BRACKET_PAIRS = (("[", "]"), ("(", ")"), ("（", "）"), ("「", "」"), ("『", "』"))

# 正規化後に全体が一致していなければならない形
_NUMBER_RE = re.compile(r"^[-+]?\d+(?:\.\d+)?$")
# 桁区切りとして認めるカンマの入り方（先頭 1〜3 桁 + 「,」+ 3 桁の繰り返し）
_GROUPED_RE = re.compile(r"^[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?$")


def extract_number(text: str | None) -> float | None:
    """回答または正解を数値として読む。読めない場合は None を返す。

    正解側・回答側の双方に同じ規則を適用するために使う。受理するのは、
    下記の正規化を施したあとに**文字列全体**が単一の数値として読める場合に
    かぎる。文字列のどこかに数字があれば採用する方式は、「1/2」を 1、
    「32 or 64」を 32 として受理してしまうため採らない。

    正規化の内容:
      - 全角数字・全角記号を半角にする
      - 囲みの括弧を 1 組だけ外す
      - 末尾の百分率記号を 1 つだけ外す
      - 桁区切りのカンマを除去する。ただし 3 桁区切りとして正しい場合に限る

    未対応（受理しない）:
      - 分数（1/2）、指数表記（1e3）、小数点前の 0 を省いた表記（.5）
      - 単位を伴う回答（32cm など）。単位の整合性を判定できないため
      - 複数の値を含む回答（32 or 64、32〜64）
    """
    if text is None:
        return None
    s = str(text).strip()
    if not s:
        return None

    # 全角数字・記号を半角へ
    s = s.translate(str.maketrans("０１２３４５６７８９．＋－，％", "0123456789.+-,%"))
    s = s.strip()

    # 囲みの括弧を 1 組だけ外す
    for left, right in _BRACKET_PAIRS:
        if s.startswith(left) and s.endswith(right) and len(s) > 2:
            s = s[len(left):-len(right)].strip()
            break

    # 末尾の百分率記号を 1 つだけ外す
    for suf in _PERCENT_SUFFIXES:
        if s.endswith(suf) and len(s) > len(suf):
            s = s[: -len(suf)].strip()
            break

    # 桁区切りのカンマは、3 桁区切りとして正しい場合にかぎり除去する。
    # 「1,2」のように 3 桁でないものは桁区切りと判断できないため受理しない。
    if "," in s:
        if not _GROUPED_RE.match(s):
            return None
        s = s.replace(",", "")

    if not _NUMBER_RE.match(s):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def resolve_choice_label(predicted: str, choices: str | None) -> str:
    """選択肢ラベル（A/B/C/D や 0〜4）を選択肢テキストに解決する。

    プロンプトはラベルでの回答を求めるが（例「回答: A」）、データセットによって
    正解が選択肢テキスト（例「包丁」）で与えられる場合とラベルで与えられる場合の
    両方がある。ラベルとして解釈できるときだけテキストに変換し、それ以外は
    入力をそのまま返す。
    """
    if not predicted or not choices:
        return predicted
    items = [c.strip() for c in choices.split("|") if c.strip()]
    if not items:
        return predicted

    token = predicted.strip()
    # 「A」「A.」「(A)」「A: 包丁」等からラベル1文字を取り出す
    m = re.match(r"^[（(\[]?\s*([A-Za-z0-9])\s*[）)\].:：、]?\s*$", token)
    if not m:
        m = re.match(r"^[（(\[]?\s*([A-Za-z0-9])\s*[）)\].:：、]\s*\S", token)
    if not m:
        return predicted

    label = m.group(1).upper()
    idx = None
    if "A" <= label <= "Z":
        idx = ord(label) - ord("A")
    elif label.isdigit():
        # 0始まり（JCommonsenseQA等）と1始まりの両方がありうる。
        # 0始まりで範囲内ならそれを優先し、駄目なら1始まりとして解釈する。
        n = int(label)
        idx = n if n < len(items) else n - 1

    if idx is None or not (0 <= idx < len(items)):
        return predicted
    return items[idx]


def judge_correctness(
    predicted: str, gold: str, answer_type: str, choices: str | None = None
) -> bool:
    """
    回答が正解かどうかを判定。
    answer_type: "mc"(多肢選択) / "numeric" / "text"
    choices: "包丁|のこぎり|ハサミ|金槌" 形式の選択肢（mc でラベル回答を解決するのに使う）
    """
    if predicted is None:
        return False
    pred = predicted.strip()
    gold = gold.strip()

    if answer_type == "numeric":
        g = extract_number(gold)
        if g is None:
            # 数値タスクなのに正解を数値として読めない。データ側の不備であり、
            # 文字列一致で正答にしてしまうと不備が見えなくなる。
            raise ValueError(
                f"answer_type='numeric' だが正解を数値として読めない: {gold!r}"
            )
        p = extract_number(pred)
        if p is None:
            # 回答が数値として読めない場合は未対応の表記として誤答扱いにする。
            # 文字列一致による救済は行わない（'1/2' と '1/2' のように、
            # 数値として解釈していないものを正答にしないため）。
            return False
        return abs(p - g) < 1e-6
    elif answer_type == "mc":
        # ラベル回答（A/B/C/D、0〜4）はまず選択肢テキストに解決してから比較する
        if gold == pred:
            return True
        resolved = resolve_choice_label(pred, choices)
        return gold in resolved or gold in pred
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
