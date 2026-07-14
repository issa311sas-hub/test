"""
中間発表スライド生成スクリプト（v3：先行研究の解説を拡充）
python generate_slides_midterm.py で .pptx を生成

構成の元ネタ: research/presentations/midterm-presentation-slide-outline.md
デザインルール: research/presentations/slide-design-rules.md を全面的に反映
  - フォントサイズは24pt未満禁止。本文は28pt基準、見出しは32〜36pt
  - グレー・薄い色の文字は使用しない（全てC_DARK/C_ACCENT/白のいずれか）
  - "⇔" は使用しない
  - 比較情報は箇条書きではなく表で表現
  - 参考文献はスライド下部に配置
  - 複数スライドにまたがる項目は (n/総数) 表記
  - 箇条書きは3項目までに制限
  - 最上部ギリギリに重要情報を置かない（ヘッダーは十分な余白を確保）

v3の変更点: 「先行研究の話が少ない」という指摘を受け、Tian et al. 2023 と
Xiong et al. 2024 をそれぞれ独立スライドで詳しく解説する。各スライドは
「先行研究の内容 → そこに残る研究の余地」という型で統一する。
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.text import MSO_ANCHOR

# --- 配色（グレー・薄色は使わない） ---
C_BG      = RGBColor(0xFF, 0xFF, 0xFF)
C_ACCENT  = RGBColor(0x1A, 0x56, 0xAA)   # 濃い青
C_ACCENT2 = RGBColor(0xB0, 0x2A, 0x1E)   # 濃い赤（強調用、プロジェクタでも視認可）
C_DARK    = RGBColor(0x14, 0x14, 0x1E)   # 本文用の濃い色（グレーではなくほぼ黒）
C_LIGHTBG = RGBColor(0xEC, 0xF1, 0xF9)   # 表の背景等（文字ではなく面のみに使用）
C_GAPBG   = RGBColor(0xFB, 0xEC, 0xEA)   # 「研究の余地」ボックスの背景（薄い赤系）
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

TOTAL_SLIDES = 19  # 本編のみ（Appendixは別カウント）


def add_rect(slide, x, y, w, h, color, line=False):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line:
        shape.line.color.rgb = C_ACCENT
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h,
             size=28, bold=False, color=C_DARK,
             align=PP_ALIGN.LEFT, wrap=True, italic=False, anchor=None):
    assert size >= 24, "フォントサイズは24pt未満禁止（slide-design-rules.md）"
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    if anchor is not None:
        tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def bullet_box(slide, lines, x, y, w, h, size=28, color=C_DARK, spacing=10, max_items=3):
    """箇条書きは3項目までを推奨（呼び出し側で担保する）"""
    assert size >= 24, "フォントサイズは24pt未満禁止（slide-design-rules.md）"
    assert len(lines) <= max_items, "箇条書きは3項目までにする（slide-design-rules.md）"
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        p.space_before = Pt(spacing)
        run = p.add_run()
        run.text = f"・{line}"
        run.font.size = Pt(size)
        run.font.color.rgb = color


def add_table(slide, headers, rows, x, y, w, h, header_size=24, body_size=24):
    """比較情報は表で表現する（slide-design-rules.md）"""
    n_rows = len(rows) + 1
    n_cols = len(headers)
    gshape = slide.shapes.add_table(n_rows, n_cols, x, y, w, h)
    table = gshape.table
    for c, htext in enumerate(headers):
        cell = table.cell(0, c)
        cell.text = htext
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_ACCENT
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.size = Pt(header_size)
                r.font.bold = True
                r.font.color.rgb = C_WHITE
    for ridx, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = table.cell(ridx, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_LIGHTBG if ridx % 2 == 0 else C_WHITE
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(body_size)
                    r.font.color.rgb = C_DARK
    return table


def header_bar(slide, title_text, slide_no=None, title_size=32):
    # 最上部ギリギリに情報を置かない：帯は0.12inchのみ、タイトルは0.32inch以降から開始
    add_rect(slide, 0, 0, W, Inches(0.12), C_ACCENT)
    add_text(slide, title_text,
             Inches(0.5), Inches(0.32), Inches(11.3), Inches(0.9),
             size=title_size, bold=True, color=C_DARK)
    if slide_no:
        add_text(slide, f"{slide_no}/{TOTAL_SLIDES}",
                 Inches(12.0), Inches(0.32), Inches(1.1), Inches(0.6),
                 size=24, color=C_ACCENT, align=PP_ALIGN.RIGHT)


def message_footer(slide, message_text):
    """1スライド1メッセージを画面下部に明示する（発表練習用の補助表示）"""
    add_rect(slide, 0, Inches(6.85), W, Inches(0.65), C_LIGHTBG)
    add_text(slide, message_text,
              Inches(0.5), Inches(6.9), Inches(12.3), Inches(0.55),
              size=24, italic=True, color=C_ACCENT)


def prior_work_slide(title, slide_no, content_lines, gap_lines, message):
    """先行研究の解説スライド：「内容→残された研究の余地」の型を強制する"""
    assert len(content_lines) <= 3
    assert len(gap_lines) <= 2
    sl = prs.slides.add_slide(BLANK)
    header_bar(sl, title, slide_no)

    add_text(sl, "先行研究の内容", Inches(0.8), Inches(1.75), Inches(11.7), Inches(0.5),
             size=26, bold=True, color=C_ACCENT)
    bullet_box(sl, content_lines, Inches(0.8), Inches(2.2), Inches(11.7), Inches(2.0),
               size=24, spacing=10)

    add_rect(sl, Inches(0.6), Inches(4.35), Inches(12.1),
             Inches(0.55 + 0.5 * len(gap_lines)), C_GAPBG)
    add_text(sl, "残された研究の余地", Inches(0.8), Inches(4.45), Inches(11.7), Inches(0.5),
             size=26, bold=True, color=C_ACCENT2)
    bullet_box(sl, gap_lines, Inches(0.8),
               Inches(4.35 + 0.55), Inches(11.7), Inches(1.3),
               size=24, spacing=8, max_items=2)

    message_footer(sl, message)
    return sl


# ══════════════════════════════════════════════════════════════
# Slide 1 — 表紙
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, C_ACCENT)
add_rect(sl, Inches(0.6), Inches(3.0), W - Inches(1.2), Inches(0.06), C_WHITE)

add_text(sl,
         "確信度プロンプト方式の比較による\nLLMキャリブレーション性能の検証",
         Inches(0.8), Inches(1.1), Inches(11.7), Inches(1.9),
         size=38, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

add_text(sl,
         "日本語ネイティブタスクにおける Verb.1S / Verb.2S / Ling.1S の比較と現行モデルでの再現性",
         Inches(0.8), Inches(2.45), Inches(11.7), Inches(0.6),
         size=24, color=C_WHITE, align=PP_ALIGN.CENTER, italic=True)

add_text(sl,
         "グループE　秦野研究室　7422048　指田一茶",
         Inches(0.8), Inches(4.4), Inches(11.7), Inches(0.7),
         size=28, color=C_WHITE, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# Slide 2 — 本日の結論（Apex）
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "本日伝えたいこと", 2)
add_rect(sl, Inches(0.8), Inches(2.3), Inches(11.7), Inches(2.0), C_LIGHTBG)
add_text(sl,
         "日本語タスクで確信度の聞き方（プロンプト方式）を変えると，\n"
         "LLMの較正精度はどう変わるかを検証する",
         Inches(1.1), Inches(2.55), Inches(11.1), Inches(1.5),
         size=32, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
add_text(sl, "研究設計・実装は完了，実験の実行はこれから",
         Inches(0.8), Inches(4.6), Inches(11.7), Inches(0.6),
         size=28, color=C_DARK, align=PP_ALIGN.CENTER)
message_footer(sl, "1メッセージ：この発表で一番伝えたい結論はこの一文")


# ══════════════════════════════════════════════════════════════
# Slide 3 — 目次
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "目次", 3)
bullet_box(sl, ["研究の背景と研究目的", "研究の方針", "現在の進捗と今後の予定"],
           Inches(1.0), Inches(2.2), Inches(10.5), Inches(3.0), size=30, spacing=24)


# ══════════════════════════════════════════════════════════════
# Slide 4 — 背景①：社会的モチベーション
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "背景①：なぜこの研究をするか", 4)
bullet_box(sl, [
    "LLMは検索・相談・意思決定支援など日常的な場面で既に使われている",
    "誤った回答を自信満々に返されると，利用者はそれを見抜けない",
    "確信度を適切に示せれば，利用者はリスクを踏まえて使い分けられる",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：この研究は誰の何の役に立つのか")


# ══════════════════════════════════════════════════════════════
# Slide 5 — 背景②：ハルシネーションとキャリブレーション
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "背景②：確信度と正答率のズレという問題", 5)
bullet_box(sl, [
    "LLMは誤情報を自信満々に生成する問題（ハルシネーション）を抱える",
    "問題の本質は「確信度」と「実際の正答率」のズレにある",
    "確信度が正答率と一致していれば（well-calibrated），判断材料になる",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：社会的な困りごとを技術的な問題設定に翻訳する")


# ══════════════════════════════════════════════════════════════
# Slide 6 — 背景③：先行研究1 Tian et al. 2023
# ══════════════════════════════════════════════════════════════
prior_work_slide(
    "背景③：先行研究1 — Tian et al. 2023", 6,
    content_lines=[
        "RLHF済みモデルは内部確率（logprob）に基づく較正が崩壊してしまう",
        "しかし「確信度をただ聞くだけ」で内部確率より良い較正が得られると発見",
        "4方式（logprob/言語表現/0-100の数値/複数候補同時提示）を比較し，数値表現が有効",
    ],
    gap_lines=[
        "検証は英語のQAタスク（TriviaQA・SciQ等）のみ",
        "日本語モデル・日本語タスクで同じ傾向が出るかは未検証",
    ],
    message="1メッセージ：「ただ聞くだけで較正が改善する」という本研究の土台と，その限界",
)


# ══════════════════════════════════════════════════════════════
# Slide 7 — 背景④：先行研究2 Xiong et al. 2024
# ══════════════════════════════════════════════════════════════
prior_work_slide(
    "背景④：先行研究2 — Xiong et al. 2024", 7,
    content_lines=[
        "Black-box確信度推定の体系的フレームワークを提案（プロンプト戦略/サンプリング/集約）",
        "5種類のデータセット×5モデルで較正精度と失敗予測を評価",
        "LLMは総じて過信しがちで，どの方式も一貫して他を上回るわけではないと報告",
    ],
    gap_lines=[
        "専門知識を要するタスクでは全手法が苦戦しており，改善の余地が大きいと自ら報告",
        "検証は英語タスクが中心で，日本語での体系的な方式間比較は行っていない",
    ],
    message="1メッセージ：確信度手法比較の先駆けだが，方式間の優劣にはまだ決着がついていない",
)


# ══════════════════════════════════════════════════════════════
# Slide 8 — 背景⑤：プロンプト設計が唯一実践可能
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "背景⑤：なぜプロンプト設計なのか", 8)
bullet_box(sl, [
    "改善手法は3系統：Post-hoc補正／ファインチューニング／プロンプト設計",
    "商用APIはlogitsやパラメータへのアクセスを提供しない",
    "一般利用者が今すぐ使える手段はプロンプト設計のみ（Xie et al. 2024）",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：数ある改善手法の中でプロンプト設計を選ぶ理由")


# ══════════════════════════════════════════════════════════════
# Slide 9 — 背景⑥：先行研究3 MlingConfとの比較
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "背景⑥：先行研究3 — MlingConfとの比較", 9)
add_text(sl, "MlingConf(Xue et al. 2025)は日本語含む5言語で確信度手法（単一方式）を検証済み",
         Inches(0.8), Inches(1.65), Inches(11.7), Inches(0.6), size=24, color=C_DARK)
add_table(sl,
          headers=["", "Tian/Xiong (英語)", "MlingConf (多言語)", "本研究"],
          rows=[
              ["対象言語", "英語のみ", "日本語含む5言語", "日本語"],
              ["方式間の比較", "なし", "なし", "あり（3方式）"],
              ["データセット", "英語標準", "英語からの機械翻訳", "日本語ネイティブ＋標準"],
              ["検証モデル", "GPT系(当時)", "GPT-3.5・Llama-3.1", "現行世代モデル"],
          ],
          x=Inches(0.6), y=Inches(2.35), w=Inches(12.1), h=Inches(3.2),
          header_size=22, body_size=22)
message_footer(sl, "1メッセージ：日本語検証は「十分に研究されていない」だけで皆無ではない")


# ══════════════════════════════════════════════════════════════
# Slide 10 — 研究目的
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究目的：主目的と付随目的", 10)
add_rect(sl, Inches(0.6), Inches(1.85), Inches(12.1), Inches(2.0), C_LIGHTBG)
add_text(sl, "主たる目的",
         Inches(0.85), Inches(1.95), Inches(11.6), Inches(0.5), size=26, bold=True, color=C_ACCENT)
add_text(sl,
         "日本語タスクで確信度プロンプト方式（Verb.1S/Verb.2S/Ling.1S）の違いは\n"
         "較正精度（ECE・Brier Score）にどのような差をもたらすか？",
         Inches(0.85), Inches(2.4), Inches(11.6), Inches(1.35), size=26, color=C_DARK)

add_rect(sl, Inches(0.6), Inches(4.05), Inches(12.1), Inches(1.7), C_BG, line=True)
add_text(sl, "付随して明らかになること",
         Inches(0.85), Inches(4.15), Inches(11.6), Inches(0.5), size=26, bold=True, color=C_ACCENT2)
add_text(sl,
         "その効果は現行世代の商用LLMでも再現されるか？",
         Inches(0.85), Inches(4.6), Inches(11.6), Inches(1.0), size=26, color=C_DARK)
message_footer(sl, "1メッセージ：主目的（方式間の差）と付随目的（再現性）を分けて示す")


# ══════════════════════════════════════════════════════════════
# Slide 11 — 方針①：実験の全体像
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "方針①：実験の全体像", 11)
bullet_box(sl, [
    "モデル：GPT-4o／Claude Sonnet 4.6／Gemini 2.x／Swallow（4〜6モデル）",
    "データセット：日本語4ドメイン × 250問 ＝ 計1,000問",
    "3つのプロンプト方式を比較（詳細は次スライド）",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：何を何で比較するかの全体像")


# ══════════════════════════════════════════════════════════════
# Slide 12 — 方針②：3方式
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "方針②：3つのプロンプト方式", 12)
add_table(sl,
          headers=["方式", "内容"],
          rows=[
              ["Verb.1S", "回答と確信度を同時に出力"],
              ["Verb.2S", "まず回答のみ回答させ，別ターンで確信度を質問"],
              ["Ling.1S", "「ほぼ確実」等の言語表現→数値マッピング"],
          ],
          x=Inches(1.2), y=Inches(2.2), w=Inches(10.9), h=Inches(3.0),
          header_size=26, body_size=26)
message_footer(sl, "1メッセージ：比較対象の3方式がそれぞれ何なのか")


# ══════════════════════════════════════════════════════════════
# Slide 13 — 方針③：評価指標の紹介
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "方針③：評価指標", 13)
bullet_box(sl, [
    "主指標：ECE（較正誤差）／Brier Score／AUROC",
    "補足的な切り口：Murphy分解（BS = REL − RES + UNC）",
    "次のスライドで主指標ECEの読み方を詳しく説明する",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：何を測るか。Murphy分解はあくまで補足")


# ══════════════════════════════════════════════════════════════
# Slide 14 — 方針④：ECEの読み方
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "方針④：ECEの読み方", 14)
add_table(sl,
          headers=["項目", "内容"],
          rows=[
              ["定義", "確信度と実際の正答率のズレの重み付き平均"],
              ["数式", "ECE = Σ (|Bm|/n) |acc(Bm) − conf(Bm)|"],
              ["値の範囲", "0以上（0〜1に収まる）"],
              ["大小の意味", "0に近いほど良い（確信度と正答率が一致）"],
              ["似た指標との違い", "Brier Scoreはビン分割不要，AUROCは識別能力を測る"],
          ],
          x=Inches(0.6), y=Inches(1.85), w=Inches(12.1), h=Inches(4.0),
          header_size=24, body_size=22)
message_footer(sl, "1メッセージ：ECEの数字が良いか悪いか自力で判断できる材料")


# ══════════════════════════════════════════════════════════════
# Slide 15 — 検証仮説（自分の予想）
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "検証仮説：自分はこう予想している", 15)
bullet_box(sl, [
    "H1：Verb.2Sは回答後に確信度を聞く分，Verb.1SよりECEが改善すると予想",
    "H2：Ling.1Sは情報を圧縮するため，数値表現方式より改善幅が小さいと予想",
    "H3：改善幅はタスクドメインにより異なると予想（正答率分布の違いのため）",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=26, spacing=16)
message_footer(sl, "1メッセージ：3つの予想とその理由（H4は質疑対応のAppendixへ）")


# ══════════════════════════════════════════════════════════════
# Slide 16 — 現在の進捗
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "現在の進捗", 16)
bullet_box(sl, [
    "プロンプト3方式×4ドメインのテンプレートと確信度の解析処理を実装済み",
    "ECE・Brier Score・AUROCの計算コードを実装し，数値的に検証済み",
    "先行研究の再調査によりMlingConfとの違いを精緻化済み",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=26, spacing=16)
message_footer(sl, "1メッセージ：準備は終わっている，実行はこれから")


# ══════════════════════════════════════════════════════════════
# Slide 17 — 今後の予定
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の予定", 17)
bullet_box(sl, [
    "パイロット実験でスクリプトの動作確認",
    "問題なければ複数モデル×3方式×大規模な問題数で本実験を実施",
    "結果はどのパターンでも報告可能な形で整理する方針",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "1メッセージ：次に何をするか")


# ══════════════════════════════════════════════════════════════
# Slide 18 — 参考文献（下部に配置）
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "参考文献", 18)
refs = [
    "Guo et al. (2017) ICML",
    "Tian et al. (2023) EMNLP",
    "Xiong et al. (2024) ICLR",
    "Xue et al. (2025) ACL Findings（MlingConf）",
    "Xie et al. (2024) arXiv（Black-Box Calibration Survey）",
    "Murphy (1973) / Bröcker (2009) / Ferro & Fricker (2012)",
]
add_text(sl, "\n".join(refs),
         Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.8),
         size=24, color=C_DARK)


# ══════════════════════════════════════════════════════════════
# Slide 19 — まとめ（表示したまま終える）
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "まとめ", 19)
bullet_box(sl, [
    "研究の問い：日本語タスクでプロンプト方式の違いは較正精度にどう影響するか",
    "現状：設計・実装は完了，実験はこれから",
    "今後：パイロット→本実験→分析→執筆",
], Inches(0.8), Inches(1.9), Inches(11.7), Inches(3.6), size=28, spacing=18)
message_footer(sl, "質疑応答中もこのスライドを表示したままにする")


prs.save("research/presentations/midterm-presentation-slides.pptx")
print("Saved: research/presentations/midterm-presentation-slides.pptx")
print(f"Total main slides: {len(prs.slides._sldIdLst)}")
