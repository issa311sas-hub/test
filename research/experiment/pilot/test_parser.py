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
    results.append(test("概数語と単位は不可", judge_correctness("約64個", "64", "numeric"), False))
    # 数値として読めない回答を正解にしない
    results.append(test("非数値の回答", judge_correctness("不明", "64", "numeric"), False))

    # ===== 回帰テスト: 2026-09-16 の追加レビュー（F01・F03）=====
    # 文字列の一部に数字があれば採用する実装は、意味の異なる回答まで
    # 受理してしまっていた。正規化後に全体が数値として読める場合のみ受理する。
    results.append(test("分数は受理しない", judge_correctness("1/2", "1", "numeric"), False))
    results.append(test("指数表記は受理しない", judge_correctness("1e3", "1", "numeric"), False))
    results.append(test("複数候補は受理しない", judge_correctness("32 or 64", "32", "numeric"), False))
    results.append(test("式は受理しない", judge_correctness("8 × 8", "8", "numeric"), False))
    results.append(test("範囲は受理しない", judge_correctness("32〜64", "32", "numeric"), False))
    # 表記上の付加は引き続き受理する
    results.append(test("全角数字", judge_correctness("１２３", "123", "numeric"), True))
    results.append(test("文末の です は不可", judge_correctness("64です", "64", "numeric"), False))
    results.append(test("概数語と単位は不可", judge_correctness("約 64 個です", "64", "numeric"), False))
    results.append(test("単位付きは不可", judge_correctness("1,200円", "1200", "numeric"), False))

    # 見出しが混在する応答では、パターンの優先順ではなく出現位置で最後を採る
    mixed = "回答: 1\nAnswer: 2\nConfidence: 0.9"
    results.append(test("見出し混在で最後を採る", parse_response(mixed).answer, "2"))

    # 仮の記入のあとに本来の回答を書く応答から、最後の回答を採る（mgsm_ja_006 等）
    two_step = "回答: [計算します]\n\n8 × 8 = 64\n\n回答: 64\n確信度: ほぼ確実"
    results.append(test("末尾の回答を採る", parse_response(two_step, mode="ling").answer, "64"))
    results.append(
        test("末尾抽出でも確信度は不変", parse_response(two_step, mode="ling").confidence, 0.95)
    )

    # ===== 回帰テスト: 2026-09-16 の検証レビュー（G02〜G07）=====
    # 単位は取り除かない。正解欄に単位が無いことは、回答の単位を消してよい
    # 理由にならない（100ドルと100セントを区別できなくなる）。
    results.append(test("単位付きは受理しない", judge_correctness("32cm", "32", "numeric"), False))
    results.append(test("単位付き(m)", judge_correctness("32m", "32", "numeric"), False))
    results.append(test("単位付き(円)", judge_correctness("32円", "32", "numeric"), False))
    # 百分率だけは例外（設問が百分率を要求し、正解が単位なしの数値のため）
    results.append(test("百分率は受理", judge_correctness("33%", "33", "numeric"), True))
    results.append(test("全角百分率", judge_correctness("33％", "33", "numeric"), True))

    # カンマは 3 桁区切りとして正しい場合のみ除去する
    results.append(test("3桁区切り", judge_correctness("1,234", "1234", "numeric"), True))
    results.append(test("2桁の区切りは不可", judge_correctness("1,23", "123", "numeric"), False))
    results.append(test("1桁の区切りは不可", judge_correctness("1,2", "12", "numeric"), False))

    # 付加の繰り返し除去を許さない
    results.append(test("単位の重複", judge_correctness("32円ドル", "32", "numeric"), False))
    results.append(test("記号の重複", judge_correctness("32%%", "32", "numeric"), False))
    results.append(test("末尾記号の重複", judge_correctness("1.2..", "1.2", "numeric"), False))

    # 未対応の表記は受理しない
    results.append(test("小数点前の0省略", judge_correctness(".5", "0.5", "numeric"), False))
    # 数値化できない回答は、正解と文字列が一致しても正答にしない
    results.append(test("非数値の一致", judge_correctness("1/2", "1", "numeric"), False))

    # 全角コロンの見出しを読める
    fw = "回答：32\n確信度：0.9"
    results.append(test("全角コロンの回答", parse_response(fw).answer, "32"))
    results.append(test("全角コロンの確信度", parse_response(fw).confidence, 0.9))

    # 確信度に % が付く場合は必ず 100 で割る
    results.append(test("確信度 0.5%", parse_response("回答: 32\n確信度: 0.5%").confidence, 0.005))
    results.append(test("確信度 75%", parse_response("回答: 32\n確信度: 75%").confidence, 0.75))
    results.append(test("確信度 0.9", parse_response("回答: 32\n確信度: 0.9").confidence, 0.9))
    results.append(test("確信度 90", parse_response("回答: 32\n確信度: 90").confidence, 0.9))

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
