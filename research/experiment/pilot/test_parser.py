"""
parser.py の単体テスト

実行方法:
  $ python test_parser.py
"""

from parser import parse_response, judge_correctness


def test(description, actual, expected):
    ok = actual == expected
    mark = "OK  " if ok else "FAIL"
    print(f"[{mark}] {description}")
    if not ok:
        print(f"       expected: {expected}")
        print(f"       actual:   {actual}")
    return ok


def main():
    results = []

    # ===== parse_response: 数値モード =====
    r = parse_response("回答: 包丁\n信頼度: 95")
    results.append(test("基本形", (r.answer, r.confidence), ("包丁", 0.95)))

    r = parse_response("回答: 東\n信頼度: 100")
    results.append(test("信頼度100", (r.answer, r.confidence), ("東", 1.0)))

    r = parse_response("回答: 不明\n信頼度: 0")
    results.append(test("信頼度0", (r.answer, r.confidence), ("不明", 0.0)))

    r = parse_response("回答: 300\n信頼度: 75%")
    results.append(test("%付き信頼度", (r.answer, r.confidence), ("300", 0.75)))

    # 英語のフォーマット
    r = parse_response("Answer: Tokyo\nConfidence: 90")
    results.append(test("英語フォーマット", (r.answer, r.confidence), ("Tokyo", 0.9)))

    # 多少の余分な文章付き
    r = parse_response("考えてみます。\n回答: 東京\n信頼度: 85\n以上です。")
    results.append(test("余分な文章付き", (r.answer, r.confidence), ("東京", 0.85)))

    # パース失敗ケース
    r = parse_response("これは答えです")
    results.append(test("失敗: フォーマットなし",
                        (r.parse_success, r.confidence), (False, None)))

    # 5段階モード
    r = parse_response("回答: A\n信頼度: 5", mode="numeric_1_5")
    results.append(test("5段階: 5", (r.answer, r.confidence), ("A", 1.0)))

    r = parse_response("回答: B\n信頼度: 1", mode="numeric_1_5")
    results.append(test("5段階: 1", (r.answer, r.confidence), ("B", 0.0)))

    r = parse_response("回答: C\n信頼度: 3", mode="numeric_1_5")
    results.append(test("5段階: 3", (r.answer, r.confidence), ("C", 0.5)))

    # 言語モード
    r = parse_response("回答: はい\n自信度: 非常に自信がある", mode="verbal")
    results.append(test("言語: 非常に自信がある",
                        (r.answer, r.confidence), ("はい", 0.95)))

    r = parse_response("回答: いいえ\n自信度: まったく自信がない", mode="verbal")
    results.append(test("言語: まったく自信がない",
                        (r.answer, r.confidence), ("いいえ", 0.05)))

    # ===== judge_correctness =====
    results.append(test("MC正解", judge_correctness("包丁", "包丁", "mc"), True))
    results.append(test("MC不正解", judge_correctness("金槌", "包丁", "mc"), False))
    results.append(test("MC含有", judge_correctness("Aの包丁", "包丁", "mc"), True))

    results.append(test("数値正解", judge_correctness("300", "300", "numeric"), True))
    results.append(test("数値カンマ付き", judge_correctness("1,000", "1000", "numeric"), True))
    results.append(test("数値不正解", judge_correctness("250", "300", "numeric"), False))
    results.append(test("数値小数", judge_correctness("28.26", "28.26", "numeric"), True))

    results.append(test("テキスト正解", judge_correctness("東京", "東京", "text"), True))
    results.append(test("テキスト含有", judge_correctness("答えは東京です", "東京", "text"), True))

    # ===== サマリー =====
    n_passed = sum(results)
    n_total = len(results)
    print(f"\n{'=' * 40}")
    print(f"結果: {n_passed}/{n_total} passed")
    print(f"{'=' * 40}")

    return 0 if n_passed == n_total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
