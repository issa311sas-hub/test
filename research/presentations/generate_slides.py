"""
2026-06-24 ゼミ発表スライド生成スクリプト（v2）
python generate_slides.py で .pptx を生成 → Google Drive にアップロードして開く

変更点 (v2):
  - 文字サイズを全体的に拡大
  - 主メッセージから環境構築・予算の話を削除（次回発表）
  - 活動報告のAI使用表現を調整
  - 前回の振り返りを3スライドに拡充（発表記録に基づく）
  - 評価指標：採用しなかった指標スライドを追加、採用指標に数式・範囲・採用理由を追加
  - データセット・正答判定に先行研究比較・理由を追加
  - プロンプト設計に専門用語説明と具体例を追加
  - 環境構築を具体的な内容に変更
  - 予算に計算式を追加
  - 参考文献にスライド番号マッピングを追加
  - 旧Appendix A/B/C を本編に移動
  - Appendix は採用しなかった指標の計算式のみ
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ===== カラーパレット =====
C_BG      = RGBColor(0xFF, 0xFF, 0xFF)
C_ACCENT  = RGBColor(0x1A, 0x56, 0xAA)
C_ACCENT2 = RGBColor(0xE8, 0x4C, 0x3C)
C_DARK    = RGBColor(0x1A, 0x1A, 0x2E)
C_GRAY    = RGBColor(0x55, 0x55, 0x55)
C_LIGHTBG = RGBColor(0xF0, 0xF4, 0xFA)
C_GREEN   = RGBColor(0x27, 0xAE, 0x60)
C_YELLOW  = RGBColor(0xF3, 0x9C, 0x12)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

TOTAL_SLIDES = 24


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
             size=24, bold=False, color=C_DARK,
             align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox


def bullet_box(slide, lines, x, y, w, h, size=22, color=C_DARK,
               indent_map=None, spacing=5):
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        level = (indent_map or {}).get(i, 0)
        p.level = level
        p.space_before = Pt(spacing)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.color.rgb = color


def header_bar(slide, title_text, slide_no=None):
    add_rect(slide, 0, 0, W, Inches(0.09), C_ACCENT)
    add_text(slide, title_text,
             Inches(0.5), Inches(0.15), Inches(11.5), Inches(0.72),
             size=30, bold=True, color=C_DARK)
    if slide_no:
        add_text(slide, f"{slide_no} / {TOTAL_SLIDES}",
                 Inches(12.0), Inches(0.15), Inches(1.1), Inches(0.6),
                 size=16, color=C_GRAY, align=PP_ALIGN.RIGHT)


def footer_bar(slide):
    add_rect(slide, 0, H - Inches(0.38), W, Inches(0.38), C_LIGHTBG)
    add_text(slide,
             "東京理科大学 経営システム工学科 秦野研究室　指田一茶　2026-06-24",
             Inches(0.3), H - Inches(0.35), Inches(13), Inches(0.32),
             size=12, color=C_GRAY)


def divider(slide, y):
    add_rect(slide, Inches(0.4), y, W - Inches(0.8), Inches(0.03), C_LIGHTBG)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 1 — 表紙
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, C_ACCENT)
add_rect(sl, Inches(0.6), Inches(2.9), W - Inches(1.2), Inches(0.06), C_BG)

add_text(sl,
         "プロンプト設計による\n大規模言語モデルの\nキャリブレーション性能向上に関する研究",
         Inches(1.0), Inches(0.9), Inches(11.3), Inches(2.8),
         size=40, bold=True, color=C_BG, align=PP_ALIGN.CENTER)

add_text(sl,
         "指田 一茶\n東京理科大学 創域理工学部 経営システム工学科 秦野研究室\n2026年6月24日 ゼミ発表",
         Inches(1.0), Inches(4.3), Inches(11.3), Inches(2.5),
         size=26, color=C_BG, align=PP_ALIGN.CENTER)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 2 — 主メッセージ（環境構築・予算は触れない）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "【本日の主メッセージ】", 2)
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(0.95), W - Inches(0.8), Inches(1.05), C_LIGHTBG)
add_text(sl,
         "研究設計の4項目が完全に確定し、来週から実験フェーズに移行できる状態になった",
         Inches(0.6), Inches(1.0), Inches(12.1), Inches(1.0),
         size=28, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)

lines = [
    "✅  評価指標の決定（ECE・Brier Score・AUROC）",
    "✅  使用データセットの選定（4ドメイン × 各 250 問 = 計 1,000 問）",
    "✅  正答判定方法の確立（ドメイン別に最適手法を選定）",
    "✅  プロンプト設計の完了（3条件: 一段階数値 / 二段階 / 言語表現）",
    "",
    "📅  次の山場：中間発表（概要 2p 提出 07/17 → 発表会 07/20〜07/27）",
]
bullet_box(sl, lines, Inches(0.8), Inches(2.1), Inches(11.8), Inches(4.8), size=24)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 3 — 目次
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "目次", 3)
footer_bar(sl)

items = [
    ("1.", "直近の活動報告"),
    ("2.", "前回の振り返り（研究背景・先行研究・RQ）"),
    ("3.", "今回の研究進捗（評価指標 / データセット / 正答判定 / プロンプト）"),
    ("4.", "今後の方向性・スケジュール"),
]
for i, (num, label) in enumerate(items):
    y = Inches(1.1) + i * Inches(1.4)
    add_rect(sl, Inches(0.5), y, Inches(0.7), Inches(1.1), C_ACCENT)
    add_text(sl, num, Inches(0.5), y + Pt(10), Inches(0.7), Inches(1.0),
             size=24, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, label, Inches(1.4), y + Pt(15), Inches(11.5), Inches(0.9),
             size=26, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 4 — 直近の活動報告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "直近の活動報告", 4)
footer_bar(sl)

lines = [
    "就活終了（結果はまだ）",
    "長期インターン完全終了（全引き継ぎ完了）→ 研究に集中できる環境に",
    "",
    "研究活動（今回）:",
    "  文献調査を中心に進め、評価指標・データセット・正答判定・プロンプト設計を検討",
    "  論文精読 12 本（Tian 2023, Xiong 2024, Yang 2024, Xue 2025 等）",
    "  各判断の根拠はメモとして記録済み",
    "  一部 AI ツールを参考程度に活用しながら調査を効率化",
    "",
    "余談：後期学費確保のため、スキマバイトの情報があればご教示ください🙏",
]
bullet_box(sl, lines, Inches(0.7), Inches(1.1), Inches(12.0), Inches(5.8),
           size=22, indent_map={4: 1, 5: 1, 6: 1, 7: 1})


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 5 — 前回の振り返り①：研究背景・テーマ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "前回の振り返り①：研究背景とテーマ", 5)
footer_bar(sl)

# 左カラム：問題意識
add_rect(sl, Inches(0.4), Inches(0.95), Inches(6.2), Inches(5.9), C_LIGHTBG)
add_text(sl, "問題意識", Inches(0.5), Inches(1.0), Inches(6.0), Inches(0.55),
         size=22, bold=True, color=C_ACCENT)
lines_l = [
    "LLM はハルシネーション（誤情報を自信",
    "ありげに生成する現象）を起こす [1]",
    "",
    "問題の本質：間違えることより",
    "「自信度と正答率の乖離」",
    "",
    "✓  90% 確信 → 約 90% 正解  ← 良い例",
    "✗  95% 確信 → 実際は誤答   ← 悪い例",
    "",
    "→ 確信度が信頼できれば、利用者が",
    "   リスク判断の指標として使えるようになる",
]
bullet_box(sl, lines_l, Inches(0.5), Inches(1.6), Inches(6.0), Inches(5.0),
           size=21, indent_map={3: 1, 4: 1, 10: 1})

# 右カラム：テーマ・キーワード
add_rect(sl, Inches(6.9), Inches(0.95), Inches(6.0), Inches(2.7), C_LIGHTBG)
add_text(sl, "研究テーマ", Inches(7.0), Inches(1.0), Inches(5.8), Inches(0.55),
         size=22, bold=True, color=C_ACCENT)
add_text(sl, "プロンプト設計による\nLLM のキャリブレーション性能向上",
         Inches(7.0), Inches(1.6), Inches(5.8), Inches(1.8),
         size=22, bold=True, color=C_DARK)

add_rect(sl, Inches(6.9), Inches(3.85), Inches(6.0), Inches(3.0), C_LIGHTBG)
add_text(sl, "キャリブレーション とは", Inches(7.0), Inches(3.9), Inches(5.8), Inches(0.55),
         size=22, bold=True, color=C_ACCENT)
add_text(sl,
         "モデルが出力する確信度と\n実際の正答率がどの程度一致しているか",
         Inches(7.0), Inches(4.5), Inches(5.8), Inches(1.2), size=21, color=C_DARK)
add_text(sl,
         "「完全キャリブレーション」=\n確信度 X% のとき、X% の確率で正解",
         Inches(7.0), Inches(5.75), Inches(5.8), Inches(0.9),
         size=18, color=C_GRAY, italic=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 6 — 前回の振り返り②：先行研究（Tian 2023）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "前回の振り返り②：重要先行研究 ── Tian et al. 2023 [3]", 6)
footer_bar(sl)

add_text(sl, "「Just Ask for Calibration」 EMNLP 2023",
         Inches(0.5), Inches(0.95), Inches(12.0), Inches(0.5),
         size=22, bold=True, color=C_ACCENT)

# 研究の概要
add_rect(sl, Inches(0.4), Inches(1.5), Inches(12.5), Inches(1.65), C_LIGHTBG)
add_text(sl, "研究の概要", Inches(0.5), Inches(1.55), Inches(4.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl,
         "ChatGPT / GPT-4 / Claude 等の RLHF 学習済み LLM に対し、確信度を「言葉」で出力させる\n"
         "（Verbalized Confidence）と、内部確率より大幅にキャリブレーションが改善することを実証。",
         Inches(0.5), Inches(2.05), Inches(12.3), Inches(1.0), size=21, color=C_DARK)

# 主な知見
results = [
    ("ECE 約 50% 削減", "直接「確信度は？」と聞くだけで、内部 softmax 確率より大幅改善"),
    ("数値 > 言語表現", "0.0〜1.0 の数値の方が「おそらく」などの言葉より精度高い"),
    ("CoT は効果なし", "Chain-of-Thought は確信度の精度に寄与しない（推論強化と混同注意）"),
    ("モデル間で差あり", "Claude 2 が最も優秀、Llama-2 はやや劣る傾向"),
]
add_text(sl, "主な知見", Inches(0.5), Inches(3.25), Inches(4.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
for i, (title, desc) in enumerate(results):
    x = Inches(0.4) + (i % 2) * Inches(6.4)
    y = Inches(3.75) + (i // 2) * Inches(1.4)
    add_rect(sl, x, y, Inches(6.0), Inches(1.2), C_LIGHTBG)
    add_text(sl, title, x + Inches(0.1), y + Pt(5), Inches(5.8), Inches(0.5),
             size=20, bold=True, color=C_DARK)
    add_text(sl, desc, x + Inches(0.1), y + Pt(28), Inches(5.8), Inches(0.7),
             size=18, color=C_GRAY)

# 本研究との関係
add_rect(sl, Inches(0.4), Inches(6.6), W - Inches(0.8), Inches(0.5), C_ACCENT)
add_text(sl,
         "本研究：この成果を日本語環境で再検証 → 英語 vs 日本語で同様の改善が得られるか？",
         Inches(0.6), Inches(6.63), Inches(12.5), Inches(0.44),
         size=19, bold=True, color=C_BG)

# Xiong 2024 補強
add_text(sl, "補強研究: Xiong et al. 2024 (ICLR) [4] が複数モデルで同様の傾向を確認",
         Inches(0.5), Inches(7.12), Inches(12.0), Inches(0.38),
         size=17, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 7 — 前回の振り返り③：RQ と実験設計の方向性
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "前回の振り返り③：RQ と実験設計の方向性", 7)
footer_bar(sl)

add_text(sl, "メイン RQ（承認済み）",
         Inches(0.4), Inches(0.95), Inches(12.5), Inches(0.5),
         size=22, bold=True, color=C_ACCENT)
add_rect(sl, Inches(0.4), Inches(1.45), W - Inches(0.8), Inches(0.9), C_LIGHTBG)
add_text(sl,
         "日本語タスクにおいて、プロンプト設計によって LLM のキャリブレーション性能を向上させられるか？",
         Inches(0.6), Inches(1.5), Inches(12.3), Inches(0.82),
         size=22, bold=True, color=C_DARK)

rqs = [
    ("RQ1", "モデル比較", "GPT / Claude / Gemini / Swallow 等でキャリブレーション性能に差はあるか"),
    ("RQ2", "タスク比較", "数学 / 常識 / 知識 / 翻訳でドメインによって性能は変化するか"),
    ("RQ3", "プロンプト比較", "確信度の引き出し方（表現形式）によって結果は変わるか"),
    ("RQ4", "言語比較", "同一タスクを日本語 vs 英語で与えた場合に差はあるか"),
]
add_text(sl, "サブ RQ", Inches(0.4), Inches(2.5), Inches(3.0), Inches(0.5),
         size=22, bold=True, color=C_ACCENT)
for i, (rq, axis, q) in enumerate(rqs):
    y = Inches(3.0) + i * Inches(0.95)
    add_rect(sl, Inches(0.4), y, Inches(1.0), Inches(0.8), C_ACCENT)
    add_text(sl, rq, Inches(0.4), y + Pt(6), Inches(1.0), Inches(0.72),
             size=18, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(1.55), y, Inches(1.9), Inches(0.8), C_LIGHTBG)
    add_text(sl, axis, Inches(1.6), y + Pt(6), Inches(1.8), Inches(0.72),
             size=18, bold=True, color=C_ACCENT)
    add_text(sl, q, Inches(3.6), y + Pt(10), Inches(9.5), Inches(0.7),
             size=20, color=C_DARK)

add_text(sl,
         "前回時点の課題（今回解決）: 評価指標の選定 / データセット選定 / 正答判定方法 / プロンプト設計",
         Inches(0.4), Inches(7.1), Inches(12.5), Inches(0.42),
         size=17, color=C_ACCENT2, italic=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 8 — 今回の進捗サマリー
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今回の進捗サマリー（4項目）", 8)
footer_bar(sl)

rows = [
    ("①", "評価指標",    "ECE（主）＋ Brier Score（副）＋ AUROC（補助）に決定"),
    ("②", "データセット", "4ドメイン × 250問 = 計 1,000問 に確定"),
    ("③", "正答判定",    "タスク別に最適手法を選定（翻訳のみ COMET 閾値）"),
    ("④", "プロンプト",  "3条件（一段階数値 / 二段階 / 言語表現）の設計完了"),
]
for i, (no, item, result) in enumerate(rows):
    y = Inches(1.1) + i * Inches(1.45)
    add_rect(sl, Inches(0.4), y, Inches(0.7), Inches(1.2), C_ACCENT)
    add_text(sl, no, Inches(0.4), y + Pt(14), Inches(0.7), Inches(1.0),
             size=26, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(1.25), y, Inches(2.4), Inches(1.2), C_LIGHTBG)
    add_text(sl, item, Inches(1.3), y + Pt(14), Inches(2.3), Inches(1.0),
             size=22, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)
    add_text(sl, result, Inches(3.85), y + Pt(16), Inches(9.2), Inches(1.0),
             size=23, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 9 — 採用しなかった評価指標（新規）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗①：評価指標の候補と不採用理由", 9)
footer_bar(sl)

add_text(sl, "（計算式・値の範囲は Appendix 参照）",
         Inches(8.0), Inches(0.9), Inches(5.0), Inches(0.45),
         size=16, color=C_GRAY, italic=True)

not_adopted = [
    ("MCE\n最大キャリブレーション誤差",
     "最大値（1ビンの外れ値）を見る指標。外れ値に過敏で全体傾向を反映しない。"
     "高リスク系（医療等）向けであり本研究の RQ には不要。"),
    ("ACE\n適応的キャリブレーション誤差",
     "等質量ビンを使いサンプル偏り問題を解決するが、ECE と互換性がなく Tian 2023 との"
     "直接比較が不能になる。"),
    ("Log-loss / NLL\n負の対数尤度",
     "理論的には Proper Scoring Rule だが、確信度が 0 や 1 に極めて近い場合に値が発散して"
     "数値的に不安定。過信傾向の強い LLM では扱いにくい。"),
    ("AUPRC\n適合率-再現率曲線下面積",
     "クラス不均衡が激しい場合に AUROC より優れるが、本研究では正答率 50〜80% 程度と不均衡が"
     "少なく AUROC で代替可能。"),
    ("AUARC\n精度-棄却曲線下面積",
     "「信頼度の低い予測から棄却した際に精度がどう上がるか」を測る指標。"
     "本研究では棄却操作を実施しないため対象外。"),
    ("SCE / cw-ECE\nクラス別 ECE",
     "多クラス分類向け指標。本研究は「正解 or 不正解」の二値問題が基本であり、"
     "クラス別拡張の追加価値が限定的。"),
]
for i, (name, reason) in enumerate(not_adopted):
    x = Inches(0.4) + (i % 2) * Inches(6.5)
    y = Inches(1.4) + (i // 2) * Inches(1.85)
    add_rect(sl, x, y, Inches(6.1), Inches(1.7), C_LIGHTBG)
    add_text(sl, name, x + Inches(0.1), y + Pt(5), Inches(5.9), Inches(0.6),
             size=19, bold=True, color=C_ACCENT2)
    add_text(sl, reason, x + Inches(0.1), y + Pt(38), Inches(5.9), Inches(1.1),
             size=17, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 10 — 採用した評価指標（概要）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗①：採用した評価指標（概要）", 10)
footer_bar(sl)

add_text(sl, "→ 詳細は次のスライドで説明",
         Inches(10.5), Inches(0.9), Inches(2.7), Inches(0.45),
         size=16, color=C_GRAY, italic=True)

metrics = [
    ("ECE\n（主指標）", C_ACCENT,
     "期待キャリブレーション誤差\nExpected Calibration Error",
     "値: 0.0〜1.0（低いほど良）",
     "先行研究 [3][4] と完全に比較可能\n「確信度と正答率のズレ」を直感的に表現"),
    ("Brier Score\n（副指標）", C_ACCENT2,
     "ブライアスコア",
     "値: 0.0〜1.0（低いほど良）",
     "厳密な Proper Scoring Rule [2]\n理論的保証が強く ECE の弱点を補完"),
    ("AUROC\n（補助指標）", C_GREEN,
     "ROC曲線下面積\nArea Under ROC Curve",
     "値: 0.5〜1.0（高いほど良）",
     "識別能力を独立に評価 [4]\nECE と直交する性質（相関≈0）"),
]
for i, (name, color, fullname, val_range, reason) in enumerate(metrics):
    x = Inches(0.4) + i * Inches(4.3)
    add_rect(sl, x, Inches(1.1), Inches(4.0), Inches(0.9), color)
    add_text(sl, name, x, Inches(1.1), Inches(4.0), Inches(0.9),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, x, Inches(2.05), Inches(4.0), Inches(4.9), C_LIGHTBG)
    add_text(sl, fullname, x + Inches(0.1), Inches(2.1), Inches(3.8), Inches(0.85),
             size=18, color=C_GRAY, italic=True)
    add_text(sl, val_range, x + Inches(0.1), Inches(3.0), Inches(3.8), Inches(0.6),
             size=19, bold=True, color=C_DARK)
    add_text(sl, reason, x + Inches(0.1), Inches(3.65), Inches(3.8), Inches(1.3),
             size=18, color=C_DARK)

add_text(sl, "可視化: Reliability Diagram（信頼性図）— 論文の Figure に必ず掲載",
         Inches(0.5), Inches(7.1), Inches(12.5), Inches(0.45),
         size=18, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 11 — ECE 詳細（旧Appendix A → 本編に移動）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "ECE（期待キャリブレーション誤差）の詳細", 11)
footer_bar(sl)

# 数式
add_rect(sl, Inches(0.4), Inches(0.95), W - Inches(0.8), Inches(1.65), C_LIGHTBG)
add_text(sl, "数式",
         Inches(0.6), Inches(1.0), Inches(2.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl, "ECE = Σ_{m=1}^{M}  ( |B_m| / n )  ×  | acc(B_m) − conf(B_m) |",
         Inches(0.7), Inches(1.48), Inches(12.0), Inches(0.95),
         size=26, bold=True, color=C_DARK)

# 変数説明
defs = [
    "B_m  : ビン m に属するサンプル集合　　　n : 総サンプル数",
    "acc(B_m)  : ビン m 内の正答率　　　　　 conf(B_m) : ビン m 内の平均確信度",
    "M = 10（等幅ビン、0.1 刻みで 0.0〜1.0 を分割）",
]
bullet_box(sl, defs, Inches(0.7), Inches(2.65), Inches(12.0), Inches(1.1), size=19)

# 値の範囲
add_rect(sl, Inches(0.4), Inches(3.85), Inches(4.0), Inches(1.35), C_LIGHTBG)
add_text(sl, "値の範囲と解釈",
         Inches(0.5), Inches(3.9), Inches(3.8), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl, "0.0 = 完全キャリブレーション\n0.1 = 確信度が正答率から平均 10% ズレ\n（低いほど良い）",
         Inches(0.5), Inches(4.42), Inches(3.8), Inches(0.75), size=19, color=C_DARK)

# 採用理由
add_rect(sl, Inches(4.6), Inches(3.85), Inches(8.3), Inches(1.35), C_LIGHTBG)
add_text(sl, "採用理由",
         Inches(4.7), Inches(3.9), Inches(8.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
lines_r = [
    "① Tian 2023 [3]・Xiong 2024 [4] と同一指標 → 先行研究の数値と直接比較可能",
    "② 「確信度と正答率の平均ズレ」という本研究の核心的問いに直接対応",
    "③ ECE=0.10 なら「平均 10% ズレ」と直感的に説明できる（発表・論文向き）",
]
bullet_box(sl, lines_r, Inches(4.7), Inches(4.4), Inches(8.0), Inches(0.75), size=18)

# 出典・補足
add_rect(sl, Inches(0.4), Inches(5.35), W - Inches(0.8), Inches(1.6), C_LIGHTBG)
add_text(sl, "出典と注意点",
         Inches(0.5), Inches(5.4), Inches(4.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
notes = [
    "出典: Guo et al. 2017 (ICML) [2] が深層学習への適用を普及させた",
    "注意: ECE は Proper Scoring Rule ではない（定数予測でも 0 になりうる）→ Brier Score で補完",
    "注意: ビン数（M）に依存。本研究では M=10 に固定し先行研究と条件を揃える",
]
bullet_box(sl, notes, Inches(0.5), Inches(5.95), Inches(12.5), Inches(0.95), size=18)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 12 — Brier Score 詳細
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Brier Score（ブライアスコア）の詳細", 12)
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(0.95), W - Inches(0.8), Inches(1.45), C_LIGHTBG)
add_text(sl, "数式",
         Inches(0.6), Inches(1.0), Inches(2.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl, "BS = (1/N) × Σ_{i=1}^{N} ( p_i − y_i )²",
         Inches(0.7), Inches(1.45), Inches(12.0), Inches(0.85),
         size=26, bold=True, color=C_DARK)

bullet_box(sl, ["p_i : モデルの確信度（0.0〜1.0）　　y_i : 正誤ラベル（正解=1, 不正解=0）"],
           Inches(0.7), Inches(2.45), Inches(12.0), Inches(0.55), size=20)

# Murphy分解
add_rect(sl, Inches(0.4), Inches(3.05), W - Inches(0.8), Inches(2.1), C_LIGHTBG)
add_text(sl, "Murphy (1973) 分解 ── Brier Score = REL − RES + UNC",
         Inches(0.5), Inches(3.1), Inches(12.5), Inches(0.55),
         size=20, bold=True, color=C_ACCENT)
comps = [
    ("REL（Reliability）", "キャリブレーション誤差", "小さいほど良", C_ACCENT2),
    ("RES（Resolution）",  "識別能力（正解・不正解を区別する能力）", "大きいほど良", C_GREEN),
    ("UNC（Uncertainty）", "データ固有の不確実性", "制御不能（固定値）", C_GRAY),
]
for i, (comp, meaning, dir_, color) in enumerate(comps):
    x = Inches(0.5) + i * Inches(4.25)
    add_rect(sl, x, Inches(3.75), Inches(3.9), Inches(1.2), color)
    add_text(sl, comp, x + Inches(0.1), Inches(3.8), Inches(3.7), Inches(0.45),
             size=17, bold=True, color=C_BG)
    add_text(sl, meaning, x + Inches(0.1), Inches(4.25), Inches(3.7), Inches(0.5),
             size=17, color=C_BG)
    add_text(sl, dir_, x + Inches(0.1), Inches(4.72), Inches(3.7), Inches(0.25),
             size=16, color=C_BG, italic=True)

# 値の範囲と採用理由
add_rect(sl, Inches(0.4), Inches(5.3), Inches(5.8), Inches(1.65), C_LIGHTBG)
add_text(sl, "値の範囲と解釈",
         Inches(0.5), Inches(5.35), Inches(5.6), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl, "0.0 = 完全予測　　0.25 = ランダム予測に相当\n（低いほど良い）",
         Inches(0.5), Inches(5.88), Inches(5.6), Inches(1.0), size=20, color=C_DARK)

add_rect(sl, Inches(6.4), Inches(5.3), Inches(6.5), Inches(1.65), C_LIGHTBG)
add_text(sl, "採用理由",
         Inches(6.5), Inches(5.35), Inches(6.3), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl,
         "① Proper Scoring Rule → ECE の理論的弱点を補完\n"
         "② ビン数に依存しない独立測定が得られる\n"
         "③ Murphy 分解で「なぜズレるか」を分離して分析できる",
         Inches(6.5), Inches(5.88), Inches(6.2), Inches(1.0), size=18, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 13 — AUROC 詳細
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "AUROC（ROC 曲線下面積）の詳細", 13)
footer_bar(sl)

add_text(sl, "AUROC = Area Under the Receiver Operating Characteristic Curve",
         Inches(0.5), Inches(0.95), Inches(12.5), Inches(0.5),
         size=19, color=C_GRAY, italic=True)

add_rect(sl, Inches(0.4), Inches(1.5), W - Inches(0.8), Inches(1.2), C_LIGHTBG)
add_text(sl, "概念的な定義（数式なし）",
         Inches(0.5), Inches(1.55), Inches(5.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl,
         "ランダムに選んだ「正解サンプル」と「不正解サンプル」のペアで、\n"
         "モデルが正解サンプルに高い確信度を与える確率",
         Inches(0.5), Inches(2.05), Inches(12.3), Inches(0.6), size=21, color=C_DARK)

# 値の解釈
add_rect(sl, Inches(0.4), Inches(2.85), Inches(5.8), Inches(1.5), C_LIGHTBG)
add_text(sl, "値の範囲と解釈",
         Inches(0.5), Inches(2.9), Inches(5.5), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl, "0.5 = ランダムと同等（確信度が意味を持たない）\n1.0 = 完全に正解・不正解を区別できる\n（高いほど良い）",
         Inches(0.5), Inches(3.42), Inches(5.6), Inches(0.88), size=19, color=C_DARK)

# ECEとの比較
add_rect(sl, Inches(6.4), Inches(2.85), Inches(6.5), Inches(1.5), C_LIGHTBG)
add_text(sl, "ECE との重要な違い",
         Inches(6.5), Inches(2.9), Inches(6.3), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
add_text(sl,
         "ECE: 「70% 確信は本当に 70% 正解か？」絶対値が重要\n"
         "AUROC: 「高確信の方が低確信より正しいか？」順序が重要\n"
         "→ 両者は独立（相関≈0）。両方報告することが推奨 [4]",
         Inches(6.5), Inches(3.42), Inches(6.3), Inches(0.88), size=18, color=C_DARK)

add_rect(sl, Inches(0.4), Inches(4.5), W - Inches(0.8), Inches(2.1), C_LIGHTBG)
add_text(sl, "採用理由",
         Inches(0.5), Inches(4.55), Inches(4.0), Inches(0.5),
         size=20, bold=True, color=C_ACCENT)
lines_au = [
    "① Xiong et al. 2024 [4] が ECE と AUROC を同時に報告しており、先行研究と比較可能",
    "② 確信度の絶対値が少しズレていても（ECE が高くても）、ランキングが正しい場合に高評価できる",
    "③ LLM の verbalized confidence は系統的な過信がある → スケール不変の AUROC で補完測定が有効",
    "④ Xiong 2024・Mind the Gap 2026 等でも ECE ＋ AUROC の組み合わせが推奨されている",
]
bullet_box(sl, lines_au, Inches(0.5), Inches(5.08), Inches(12.3), Inches(1.45), size=19)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 14 — データセット選定（先行研究比較・問題数の根拠）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗②：データセットの選定", 14)
footer_bar(sl)

add_text(sl, "各 250 問 × 4 ドメイン = 合計 1,000 問",
         Inches(0.5), Inches(0.92), Inches(8.0), Inches(0.5),
         size=22, bold=True, color=C_ACCENT)

datasets = [
    ("数学",  "MGSM",           "GSM8K（英語）の人手翻訳版",
     "先行研究（Tian 2023, MlingConf 2025）でも GSM8K 使用。本研究は日本語対応の MGSM を選択"),
    ("常識",  "JCommonsenseQA", "日本語ネイティブ作成 5択MC",
     "Xiong 2024 が CommonsenseQA（英語）を使用。日本語対応版として JCommonsenseQA を採用"),
    ("知識",  "JMMLU",          "日本人教師作成・日本史中心 4択MC",
     "先行研究は MMLU（英語）使用。日本語対応版 JMMLU（nlp-waseda）を採用"),
    ("翻訳",  "FLORES-200",     "Meta AI 公開の対訳データセット",
     "翻訳ドメインを評価するのは本研究の新規性。MlingConf 2025 でも使用実績あり"),
]
for i, (domain, name, desc, reason) in enumerate(datasets):
    y = Inches(1.5) + i * Inches(1.3)
    add_rect(sl, Inches(0.4), y, Inches(1.5), Inches(1.1), C_ACCENT)
    add_text(sl, domain, Inches(0.4), y + Pt(12), Inches(1.5), Inches(0.95),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(2.05), y, Inches(11.05), Inches(1.1), C_LIGHTBG)
    add_text(sl, f"{name}  ─  {desc}",
             Inches(2.15), y + Pt(6), Inches(10.8), Inches(0.45),
             size=20, bold=True, color=C_DARK)
    add_text(sl, f"▸ {reason}",
             Inches(2.15), y + Pt(36), Inches(10.8), Inches(0.55),
             size=18, color=C_GRAY)

# 問題数の根拠
add_rect(sl, Inches(0.4), Inches(6.75), W - Inches(0.8), Inches(0.85), C_ACCENT2)
add_text(sl,
         "なぜ 250 問か？ECE（10 ビン）で各ビン最低 25 問を確保するための下限。"
         "旧計画（25問/ドメイン）では ECE の統計的信頼性がほぼなかった（各ビン 2〜3 問しかない）。",
         Inches(0.6), Inches(6.78), Inches(12.5), Inches(0.8),
         size=18, bold=False, color=C_BG)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 15 — 正答判定（COMET正式名称・先行研究比較）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗③：正答判定方法の確立", 15)
footer_bar(sl)

add_text(sl, "正答判定は「正解/不正解（y=1 or y=0）」の二値ラベルを付ける作業。ECE 計算の起点となる最重要設計。",
         Inches(0.4), Inches(0.92), Inches(12.8), Inches(0.5),
         size=19, color=C_GRAY)

judgments = [
    ("数学\nMGSM",      "正規化完全一致",
     "正規表現で数値抽出 → 正解値と比較",
     "先行研究（ConfTuner 2025 等）が GSM8K で採用している標準手法。数値の完全一致なので判定ノイズなし"),
    ("常識・知識\nJC-QA / JMMLU", "選択肢ラベル一致",
     "出力ラベル（A/B/C/D など）を正解と比較",
     "MC 形式は calibration 研究の 60〜70% が採用する最も信頼性の高い判定方法（Xiong 2024 [4] 等）"),
    ("翻訳\nFLORES-200",   "COMET スコア閾値",
     "COMET スコア ≥ θ（人間 50 文で F1 最適化）",
     "BLEU は廃れつつあり COMET が現在の主流。閾値 ±0.05 の感度分析も実施"),
]
for i, (domain, method, how, reason) in enumerate(judgments):
    y = Inches(1.5) + i * Inches(1.85)
    add_rect(sl, Inches(0.4), y, Inches(2.2), Inches(1.65), C_ACCENT)
    add_text(sl, domain, Inches(0.4), y + Pt(14), Inches(2.2), Inches(1.45),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(2.75), y, Inches(10.3), Inches(1.65), C_LIGHTBG)
    add_text(sl, method, Inches(2.85), y + Pt(6), Inches(10.0), Inches(0.5),
             size=22, bold=True, color=C_DARK)
    add_text(sl, f"方法: {how}", Inches(2.85), y + Pt(40), Inches(10.0), Inches(0.45),
             size=19, color=C_ACCENT2)
    add_text(sl, f"理由: {reason}", Inches(2.85), y + Pt(68), Inches(10.0), Inches(0.55),
             size=17, color=C_GRAY)

# COMET 説明
add_rect(sl, Inches(0.4), Inches(7.1), W - Inches(0.8), Inches(0.47), C_LIGHTBG)
add_text(sl,
         "※ COMET = Crosslingual Optimized Metric for Evaluation of Translation"
         "（機械翻訳品質評価のニューラルメトリクス。人間評価との相関が BLEU より高い）",
         Inches(0.6), Inches(7.12), Inches(12.5), Inches(0.43),
         size=16, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 16 — プロンプト設計概要
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗④：プロンプト設計の概要", 16)
footer_bar(sl)

add_text(sl, "確信度の「引き出し方」を変えることでキャリブレーション性能がどう変わるかを比較する",
         Inches(0.4), Inches(0.92), Inches(12.8), Inches(0.5),
         size=20, color=C_GRAY)

conds = [
    ("Verb.1S\nVerbalized 1-Stage",
     "Verbalized（言語化）の 1-Stage（1段階）",
     "回答と確信度（0.0〜1.0）を1回のプロンプトで同時出力",
     "Xiong 2024 [4] の Vanilla 方式に対応",
     C_ACCENT),
    ("Verb.2S\nVerbalized 2-Stage",
     "Verbalized（言語化）の 2-Stage（2段階）",
     "Turn 1 で回答のみ → Turn 2 で「その確信度は？」と別途質問（2コール/問）",
     "Tian 2023 [3] の Two-Stage / Xiong 2024 [4] の Self-Probing に対応",
     C_ACCENT2),
    ("Ling.1S\nLinguistic 1-Stage",
     "Linguistic（言語表現）の 1-Stage（1段階）",
     "「ほぼ確実」「かなり自信がある」等の言葉で確信度を表現 → 数値に変換",
     "Tian 2023 [3] の Linguistic 方式に対応",
     C_GREEN),
]
for i, (name, abbr_meaning, desc, ref, color) in enumerate(conds):
    x = Inches(0.4) + i * Inches(4.3)
    add_rect(sl, x, Inches(1.5), Inches(4.05), Inches(1.0), color)
    add_text(sl, name, x, Inches(1.5), Inches(4.05), Inches(1.0),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, x, Inches(2.55), Inches(4.05), Inches(4.55), C_LIGHTBG)
    add_text(sl, f"略語の意味: {abbr_meaning}",
             x + Inches(0.1), Inches(2.6), Inches(3.85), Inches(0.6),
             size=16, color=C_GRAY, italic=True)
    add_text(sl, desc,
             x + Inches(0.1), Inches(3.25), Inches(3.85), Inches(1.4),
             size=19, color=C_DARK)
    add_text(sl, ref,
             x + Inches(0.1), Inches(4.65), Inches(3.85), Inches(0.42),
             size=16, color=C_ACCENT2)

add_rect(sl, Inches(0.4), Inches(7.1), W - Inches(0.8), Inches(0.47), C_LIGHTBG)
add_text(sl,
         "注: CoT（Chain-of-Thought）は独立条件としない。正答率自体を変化させるため、確信度設計の効果と分離困難。",
         Inches(0.6), Inches(7.13), Inches(12.5), Inches(0.43),
         size=16, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 17 — プロンプト具体例（旧Appendix B → 本編に移動）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "プロンプト具体例（数学ドメイン版）", 17)
footer_bar(sl)

examples = [
    ("Verb.1S", C_ACCENT,
     "以下の数学の問題を読み、回答と確信度を答えてください。\n"
     "確信度は 0.0（自信なし）〜1.0（完全に確信）で表してください。\n"
     "問題: {question}\n"
     "形式: 回答: [数値のみ]　確信度: [0.0〜1.0]"),
    ("Verb.2S  ターン1", C_ACCENT2,
     "以下の問題に回答してください。\n"
     "問題: {question}\n"
     "形式: 回答: [数値のみ]"),
    ("Verb.2S  ターン2", C_ACCENT2,
     "あなたは先ほど「{answer}」と回答しました。\n"
     "この回答が正しい確率を 0.0〜1.0 で答えてください。\n"
     "形式: 確信度: [0.0〜1.0]"),
    ("Ling.1S", C_GREEN,
     "問題: {question}\n"
     "回答と、確信の度合い（ほぼ確実 / かなり自信がある / どちらともいえない\n"
     "/ あまり自信がない / ほとんどわからない）を答えてください。\n"
     "形式: 回答: [数値のみ]　確信度: [上記5つから1つ]"),
]
for i, (label, color, prompt) in enumerate(examples):
    x = Inches(0.4) + (i % 2) * Inches(6.5)
    y = Inches(1.05) + (i // 2) * Inches(3.15)
    add_rect(sl, x, y, Inches(0.15), Inches(2.8), color)
    add_rect(sl, x + Inches(0.2), y, Inches(1.5), Inches(0.45), color)
    add_text(sl, label, x + Inches(0.22), y + Pt(2), Inches(1.48), Inches(0.43),
             size=16, bold=True, color=C_BG)
    add_rect(sl, x + Inches(0.2), y + Inches(0.45), Inches(6.0), Inches(2.35), C_LIGHTBG)
    add_text(sl, prompt,
             x + Inches(0.3), y + Inches(0.5), Inches(5.85), Inches(2.2),
             size=17, color=C_DARK)

add_text(sl, "Ling.1S の数値マッピング:  ほぼ確実=0.95 / かなり=0.80 / どちらとも=0.50 / あまり=0.25 / ほとんどわからない=0.05",
         Inches(0.4), Inches(7.1), W - Inches(0.4), Inches(0.45),
         size=17, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 18 — 着地地点の複数構想
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の方向性①：着地地点の複数構想", 18)
footer_bar(sl)

add_text(sl, "先生のご指摘：「ライバルが出てきそうなので着地地点を複数用意すべき」",
         Inches(0.5), Inches(0.92), Inches(12.5), Inches(0.5),
         size=20, color=C_GRAY, italic=True)

plans = [
    ("A（本命）",    C_GREEN,   "予定通り進捗",      "日本語 × 複数モデル × 3手法の全比較 → 最適プロンプト方式を提案"),
    ("B",           C_ACCENT,  "ECE 差が有意でない", "ネガティブ結果の体系的報告（「差がない」ことの証明も学術貢献）"),
    ("C",           C_ACCENT2, "競合研究が先行発表", "翻訳ドメイン（COMET × 確信度）に絞り込んで独自深掘り"),
    ("D",           C_GRAY,    "11月末に進捗不足",   "スコープ縮小トリガー発動（文書化済み）→ モデル・ドメイン数を削減"),
]
for i, (name, color, cond, content) in enumerate(plans):
    y = Inches(1.5) + i * Inches(1.35)
    add_rect(sl, Inches(0.4), y, Inches(1.6), Inches(1.2), color)
    add_text(sl, name, Inches(0.4), y + Pt(14), Inches(1.6), Inches(1.05),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(2.15), y, Inches(2.8), Inches(1.2), C_LIGHTBG)
    add_text(sl, cond, Inches(2.25), y + Pt(14), Inches(2.6), Inches(1.0),
             size=18, color=C_GRAY)
    add_text(sl, content, Inches(5.15), y + Pt(14), Inches(8.0), Inches(1.0),
             size=21, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 19 — 予算見積もり（計算式付き）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の方向性②：予算見積もり（確定版）", 19)
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(0.92), W - Inches(0.8), Inches(0.7), C_LIGHTBG)
add_text(sl, "実験全体の合計：約 $20 USD ≈ 3,000 円（×2倍バッファ込み）　研究室枠 50,000 円の 6%",
         Inches(0.6), Inches(0.95), Inches(12.5), Inches(0.65),
         size=22, bold=True, color=C_ACCENT)

# 料金表
add_text(sl, "各モデルの料金（2026年6月現在）",
         Inches(0.5), Inches(1.72), Inches(6.5), Inches(0.45),
         size=19, bold=True, color=C_DARK)
models = [
    ("Claude Sonnet 4.6", "$3.00", "$15.00"),
    ("GPT-4o",            "$2.50", "$10.00"),
    ("GPT-5",             "$0.63", "$5.00"),
    ("Gemini 2.0 Flash",  "$0.15", "$0.60"),
]
for i, (model, inp, out) in enumerate(models):
    y = Inches(2.2) + i * Inches(0.52)
    bg = C_LIGHTBG if i % 2 == 0 else C_BG
    add_rect(sl, Inches(0.4), y, Inches(6.2), Inches(0.5), bg)
    add_text(sl, model, Inches(0.5), y + Pt(4), Inches(3.5), Inches(0.44), size=18, color=C_DARK)
    add_text(sl, inp,   Inches(4.0), y + Pt(4), Inches(1.4), Inches(0.44), size=18, color=C_DARK)
    add_text(sl, out,   Inches(5.4), y + Pt(4), Inches(1.4), Inches(0.44), size=18, color=C_DARK)
add_text(sl, "モデル             入力$/1M   出力$/1M",
         Inches(0.5), Inches(2.18), Inches(6.0), Inches(0.42), size=16, color=C_GRAY)

# 計算式
add_rect(sl, Inches(6.8), Inches(1.72), Inches(6.2), Inches(3.15), C_LIGHTBG)
add_text(sl, "計算式（コール当たりのコスト）",
         Inches(6.9), Inches(1.77), Inches(5.9), Inches(0.45),
         size=19, bold=True, color=C_ACCENT)
add_text(sl,
         "コール当たり: 入力 300 tokens + 出力 50 tokens と仮定\n\n"
         "例: Claude Sonnet 4.6 / 1,000 コール\n"
         "  入力: 1,000 × 300 / 1,000,000 × $3.00 = $0.90\n"
         "  出力: 1,000 × 50  / 1,000,000 × $15.00 = $0.75\n"
         "  小計: $1.65\n\n"
         "実験①（4モデル×各1,000コール）: 約 $3.40\n"
         "実験②（追加3,000コール）:        約 $5.00\n"
         "実験③（追加1,000コール）:        約 $1.65\n"
         "合計 × 2倍バッファ: 約 $20 ≈ 3,000円",
         Inches(6.9), Inches(2.25), Inches(5.9), Inches(2.55), size=17, color=C_DARK)

add_text(sl, "OSS モデル（Swallow・ELYZA・Qwen）はローカル実行 → 追加費用なし",
         Inches(0.5), Inches(7.1), Inches(12.5), Inches(0.45),
         size=17, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 20 — 実験環境構築（具体的な内容）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の方向性③：実験環境の構築", 20)
footer_bar(sl)

steps = [
    ("① Python 環境の整備",
     "Python 3.12 + Anaconda（or venv）で仮想環境を作成\n"
     "必要ライブラリをインストール: openai / anthropic / google-generativeai\n"
     "                               datasets / netcal / scikit-learn / unbabel-comet"),
    ("② API キーの取得と設定",
     "各サービスで API キーを取得（OpenAI / Anthropic / Google AI Studio）\n"
     "環境変数（.env ファイル）に登録し、スクリプトから安全に参照"),
    ("③ データセットの前処理",
     "HuggingFace datasets で MGSM / JCommonsenseQA / JMMLU / FLORES-200 をダウンロード\n"
     "各 250 問をサンプリングし、正解ラベル付き CSV として保存"),
    ("④ 実験スクリプトの設計",
     "問題 CSV → API 問い合わせ（プロンプト条件ごとに分岐）→ 回答・確信度 CSV 保存\n"
     "→ 正誤判定スクリプト → ECE / Brier / AUROC 計算 → Reliability Diagram 出力"),
]
for i, (title, detail) in enumerate(steps):
    y = Inches(1.05) + i * Inches(1.55)
    add_rect(sl, Inches(0.4), y, Inches(3.2), Inches(1.35), C_ACCENT)
    add_text(sl, title, Inches(0.45), y + Pt(10), Inches(3.1), Inches(1.2),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(3.75), y, Inches(9.2), Inches(1.35), C_LIGHTBG)
    add_text(sl, detail, Inches(3.85), y + Pt(8), Inches(9.0), Inches(1.2),
             size=18, color=C_DARK)

add_text(sl, "目標: 7月中旬（中間発表前）にパイロット実験（1ドメイン × 1モデル × 1条件）で動作確認完了",
         Inches(0.4), Inches(7.1), Inches(12.8), Inches(0.45),
         size=17, bold=True, color=C_ACCENT2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 21 — スケジュール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後のスケジュール", 21)
footer_bar(sl)

schedule = [
    ("6月（残り）",     C_ACCENT,   "実験スクリプト実装・パイロット実験（動作確認）"),
    ("7月 17日 ⚠️",     C_ACCENT2,  "中間発表 概要 2p PDF 提出（LETUS 12:00 厳守）"),
    ("7月 20〜27日 ⚠️", C_ACCENT2,  "中間発表会（6分＋質疑3分）"),
    ("8〜9月",          C_ACCENT,   "本実験（4ドメイン × 4モデル × 3プロンプト方式）"),
    ("10月",            C_ACCENT,   "結果分析・統計検定（Friedman 検定 / Wilcoxon 検定）"),
    ("11月〜1月",       C_GREEN,    "論文執筆・提出"),
]
for i, (period, color, task) in enumerate(schedule):
    y = Inches(1.05) + i * Inches(1.02)
    add_rect(sl, Inches(0.4), y, Inches(2.5), Inches(0.9), color)
    add_text(sl, period, Inches(0.4), y + Pt(8), Inches(2.5), Inches(0.82),
             size=19, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, task, Inches(3.1), y + Pt(10), Inches(10.2), Inches(0.8),
             size=22, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 22 — 参考文献（スライド番号マッピング付き）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "参考文献", 22)
footer_bar(sl)

refs = [
    ("[1]", "Ji, Z. et al. (2023). Survey of Hallucination in NLG. ACM Computing Surveys.",
     "→ Slide 5（研究背景）"),
    ("[2]", "Guo, C. et al. (2017). On Calibration of Modern Neural Networks. ICML.",
     "→ Slide 10, 11（ECE の出典）"),
    ("[3]", "Tian, K. et al. (2023). Just Ask for Calibration. EMNLP.",
     "→ Slide 6, 9, 10, 14, 16（主要先行研究・全体）"),
    ("[4]", "Xiong, M. et al. (2024). Can LLMs Express Their Uncertainty? ICLR.",
     "→ Slide 6, 10, 13, 14, 16（先行研究・AUROC）"),
    ("[5]", "Kadavath, S. et al. (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221.",
     "→ Slide 5（研究背景）"),
    ("[6]", "Zheng, L. et al. (2023). Judging LLM-as-a-Judge with MT-Bench. NeurIPS.",
     "→ Slide 15（翻訳の正答判定）"),
    ("[7]", "Yang, D. et al. (2024). On Verbalized Confidence Scores for LLMs. arXiv:2412.14737.",
     "→ Slide 16（プロンプト設計の根拠）"),
    ("[8]", "Xue, B. et al. (2025). MlingConf: Multilingual Confidence Estimation. ACL Findings.",
     "→ Slide 6, 7, 14（多言語キャリブレーション）"),
    ("[9]", "Seo, K. J. et al. (2025). ADVICE: Answer-Dependent Verbalized Confidence. arXiv:2510.10913.",
     "→ Slide 16（Verb.2S の設計根拠）"),
    ("[10]", "Li, Y. et al. (2025). ConfTuner: Training LLMs to Express Confidence. arXiv:2508.18847.",
     "→ Slide 10, 14（Brier Score の採用根拠）"),
]
for i, (num, text, slide_ref) in enumerate(refs):
    y = Inches(0.98) + i * Inches(0.63)
    add_text(sl, num, Inches(0.4), y, Inches(0.55), Inches(0.58),
             size=17, bold=True, color=C_ACCENT)
    add_text(sl, text, Inches(1.0), y, Inches(9.8), Inches(0.58), size=17, color=C_DARK)
    add_text(sl, slide_ref, Inches(10.9), y, Inches(2.2), Inches(0.58),
             size=15, color=C_GRAY, italic=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 23 — 実験計画全体像（旧Appendix C → 本編に移動）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "実験計画の全体像", 23)
footer_bar(sl)

exp_rows = [
    ("実験①\n基本\nキャリブレーション",
     "Verb.1S × 4 商用モデル × 1,000 問",
     "4 モデル（Claude / GPT-4o / GPT-5 / Gemini）間での\nキャリブレーション差を測定（RQ1・RQ2）",
     "4,000"),
    ("実験②\nプロンプト\n手法比較",
     "Verb.2S + Ling.1S × 1 モデル × 1,000 問",
     "3 プロンプト方式の比較（RQ3）\nVerb.2S は 2 コール/問なので 2,000 コール",
     "3,000"),
    ("実験③\n日英\n比較",
     "英語版 × 1 モデル × 1,000 問",
     "日本語と英語で同一タスクを比較（RQ4）\n英語対応データセットで同条件実施",
     "1,000"),
]
add_text(sl, "実験", Inches(0.4), Inches(0.95), Inches(2.5), Inches(0.45),
         size=18, bold=True, color=C_GRAY)
add_text(sl, "条件", Inches(3.0), Inches(0.95), Inches(4.3), Inches(0.45),
         size=18, bold=True, color=C_GRAY)
add_text(sl, "目的と対応 RQ", Inches(7.5), Inches(0.95), Inches(4.8), Inches(0.45),
         size=18, bold=True, color=C_GRAY)
add_text(sl, "コール数", Inches(12.5), Inches(0.95), Inches(0.8), Inches(0.45),
         size=18, bold=True, color=C_GRAY)

for i, (name, cond, purpose, calls) in enumerate(exp_rows):
    y = Inches(1.45) + i * Inches(1.85)
    add_rect(sl, Inches(0.4), y, Inches(2.4), Inches(1.65), C_ACCENT)
    add_text(sl, name, Inches(0.4), y + Pt(12), Inches(2.4), Inches(1.5),
             size=18, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(3.0), y, Inches(4.3), Inches(1.65), C_LIGHTBG)
    add_text(sl, cond, Inches(3.1), y + Pt(10), Inches(4.1), Inches(1.5), size=18, color=C_DARK)
    add_rect(sl, Inches(7.5), y, Inches(4.8), Inches(1.65), C_LIGHTBG)
    add_text(sl, purpose, Inches(7.6), y + Pt(10), Inches(4.6), Inches(1.5), size=17, color=C_DARK)
    add_text(sl, calls, Inches(12.4), y + Pt(25), Inches(0.9), Inches(1.0),
             size=22, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)

add_rect(sl, Inches(0.4), Inches(7.1), W - Inches(0.8), Inches(0.47), C_ACCENT)
add_text(sl,
         "合計 8,000 コール（×2 倍バッファ含む 16,000 コール）　≈  $20 USD  ≈  3,000 円",
         Inches(0.6), Inches(7.12), Inches(12.5), Inches(0.43),
         size=19, bold=True, color=C_BG)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 24 — Appendix: 採用しなかった指標の計算式
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Appendix：採用しなかった指標の計算式", 24)
footer_bar(sl)

add_text(sl, "（値の範囲・採用しなかった理由はスライド 9 参照）",
         Inches(0.4), Inches(0.92), Inches(12.5), Inches(0.45),
         size=17, color=C_GRAY, italic=True)

formulas = [
    ("MCE",
     "MCE = max_{m=1,...,M} | acc(B_m) − conf(B_m) |",
     "等幅ビン M=10。重み付き平均の代わりに最大値を取る。"),
    ("ACE",
     "ACE = Σ_{m=1}^{M} (1/M) × | acc(B_m) − conf(B_m) |",
     "等質量ビン（各ビンのサンプル数を均等化）。ECE の 1/M は等質量ビンの場合に成立。"),
    ("Log-loss / NLL",
     "NLL = −(1/N) × Σ_{i=1}^{N} [ y_i·log(p_i) + (1−y_i)·log(1−p_i) ]",
     "p_i→0 や p_i→1 のとき値が発散。LLM の過信傾向で不安定になりやすい。"),
    ("SCE / cw-ECE",
     "SCE = (1/K) × Σ_{k=1}^{K} Σ_{b=1}^{B} (n_{b,k}/N) × | acc(b,k) − conf(b,k) |",
     "K はクラス数。本研究は正解/不正解の二値なのでクラス別拡張は不要。"),
]
for i, (name, formula, note) in enumerate(formulas):
    y = Inches(1.45) + i * Inches(1.45)
    add_rect(sl, Inches(0.4), y, Inches(2.0), Inches(1.25), C_ACCENT2)
    add_text(sl, name, Inches(0.4), y + Pt(16), Inches(2.0), Inches(1.1),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(2.55), y, Inches(10.5), Inches(1.25), C_LIGHTBG)
    add_text(sl, formula, Inches(2.65), y + Pt(6), Inches(10.2), Inches(0.55),
             size=18, bold=True, color=C_DARK)
    add_text(sl, note, Inches(2.65), y + Pt(42), Inches(10.2), Inches(0.55),
             size=17, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 保存
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT = "2026-06-24-seminar-slides.pptx"
prs.save(OUTPUT)
print(f"✅  {OUTPUT} を生成しました（{len(prs.slides)} スライド）")
