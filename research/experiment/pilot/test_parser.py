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

    # ===== 回帰テスト: 2026-09-16 のレビューで発見された採点の不具合 =====
    # 正解側のカンマを除去していなかったため数値比較に失敗し、部分一致に
    # 落ちて正解が誤答と記録されていた（mgsm_ja_147 等）
    results.append(test("正解側カンマ", judge_correctness("2125", "2,125", "numeric"), True))
    results.append(test("正解側カンマ大", judge_correctness("114200", "114,200", "numeric"), True))
    results.append(test("双方カンマ", judge_correctness("2,125", "2,125", "numeric"), True))
    results.append(test("カンマ付き誤答", judge_correctness("2125", "2,126", "numeric"), False))
    # 書式上の付加がある正解を取りこぼさない
    results.append(test("百分率表記", judge_correctness("33%", "33", "numeric"), True))
    results.append(test("括弧付き", judge_correctness("[32]", "32", "numeric"), True))
    results.append(test("単位付き", judge_correctness("約64個", "64", "numeric"), True))
    # 数値として読めない回答を正解にしない
    results.append(test("非数値の回答", judge_correctness("不明", "64", "numeric"), False))

    # 仮の記入のあとに本来の回答を書く応答から、最後の回答を採る（mgsm_ja_006 等）
    two_step = "回答: [計算します]\n\n8 × 8 = 64\n\n回答: 64\n確信度: ほぼ確実"
    results.append(test("末尾の回答を採る", parse_response(two_step, mode="ling").answer, "64"))
    results.append(
        test("末尾抽出でも確信度は不変", parse_response(two_step, mode="ling").confidence, 0.95)
    )

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
