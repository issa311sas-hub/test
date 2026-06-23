"""
2026-06-24 ゼミ発表スライド生成スクリプト
python generate_slides.py で .pptx を生成 → Google Drive にアップロードして開く
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ===== カラーパレット =====
C_BG       = RGBColor(0xFF, 0xFF, 0xFF)   # 白背景
C_ACCENT   = RGBColor(0x1A, 0x56, 0xAA)   # 東京理科大ブルー
C_ACCENT2  = RGBColor(0xE8, 0x4C, 0x3C)   # 強調レッド
C_DARK     = RGBColor(0x1A, 0x1A, 0x2E)   # 見出し濃紺
C_GRAY     = RGBColor(0x55, 0x55, 0x55)   # 本文グレー
C_LIGHTBG  = RGBColor(0xF0, 0xF4, 0xFA)   # 薄青背景
C_GREEN    = RGBColor(0x27, 0xAE, 0x60)   # チェックマーク緑

W = Inches(13.33)   # 16:9 横幅
H = Inches(7.5)     # 16:9 縦幅

prs = Presentation()
prs.slide_width  = W
prs.slide_height = H

BLANK = prs.slide_layouts[6]   # 完全ブランク


def add_rect(slide, x, y, w, h, color):
    shape = slide.shapes.add_shape(1, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h,
             size=24, bold=False, color=C_DARK,
             align=PP_ALIGN.LEFT, wrap=True):
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def header_bar(slide, title_text, slide_no=None, total=19):
    """上部アクセントバー＋タイトル"""
    add_rect(slide, 0, 0, W, Inches(0.08), C_ACCENT)
    tx = slide.shapes.add_textbox(Inches(0.5), Inches(0.15), Inches(11.5), Inches(0.7))
    tf = tx.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title_text
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = C_DARK
    if slide_no:
        sn = slide.shapes.add_textbox(Inches(12.3), Inches(0.15), Inches(0.8), Inches(0.5))
        tf2 = sn.text_frame
        p2 = tf2.paragraphs[0]
        p2.alignment = PP_ALIGN.RIGHT
        r2 = p2.add_run()
        r2.text = f"{slide_no}/{total}"
        r2.font.size = Pt(14)
        r2.font.color.rgb = C_GRAY


def footer_bar(slide):
    add_rect(slide, 0, H - Inches(0.35), W, Inches(0.35), C_LIGHTBG)
    add_text(slide,
             "東京理科大学 経営システム工学科 秦野研究室　指田一茶　2026-06-24",
             Inches(0.3), H - Inches(0.32), Inches(12), Inches(0.28),
             size=10, color=C_GRAY)


def bullet_lines(slide, lines, x, y, w, h, size=20, indent_map=None):
    """箇条書きを追加する（indent_map: {行番号: レベル} で字下げ制御）"""
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        level = (indent_map or {}).get(i, 0)
        p.level = level
        p.space_before = Pt(4)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.color.rgb = C_DARK


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 1 — 表紙
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, C_ACCENT)
add_rect(sl, Inches(0.5), Inches(2.8), W - Inches(1), Inches(0.06), C_BG)

add_text(sl,
         "プロンプト設計による\n大規模言語モデルの\nキャリブレーション性能向上に関する研究",
         Inches(1), Inches(1.0), Inches(11.3), Inches(2.5),
         size=36, bold=True, color=C_BG, align=PP_ALIGN.CENTER)

add_text(sl,
         "指田 一茶\n東京理科大学 創域理工学部 経営システム工学科 秦野研究室\n2026年6月24日 ゼミ発表",
         Inches(1), Inches(4.5), Inches(11.3), Inches(2.5),
         size=22, color=C_BG, align=PP_ALIGN.CENTER)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 2 — 主メッセージ（Apex）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "【本日の主メッセージ】", 2)
footer_bar(sl)

add_rect(sl, Inches(0.5), Inches(0.95), W - Inches(1), Inches(1.1), C_LIGHTBG)
add_text(sl,
         "研究設計が完全に確定し、来週から実験フェーズに移行できる状態になった",
         Inches(0.7), Inches(1.0), Inches(11.9), Inches(1.0),
         size=26, bold=True, color=C_ACCENT, align=PP_ALIGN.CENTER)

bullets = [
    "✅  評価指標・データセット・正答判定・プロンプト設計の 4 項目が確定",
    "✅  実験環境の構築方針（ツール・インストール手順）が整備済み",
    "✅  予算：研究室枠（50,000円）の 約 6 % 以内（約 3,000 円）で完結",
    "📅  次の山場：中間発表（概要2p提出 07/17 → 発表会 07/20〜07/27）",
]
bullet_lines(sl, bullets, Inches(0.8), Inches(2.2), Inches(11.7), Inches(4.5), size=22)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 3 — 目次
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "目次", 3)
footer_bar(sl)

items = [
    ("1.", "直近の活動報告"),
    ("2.", "前回の振り返り"),
    ("3.", "今回の研究進捗（4項目）"),
    ("4.", "次フェーズへの移行状況"),
    ("5.", "今後の方向性・スケジュール"),
]
for i, (num, label) in enumerate(items):
    y = Inches(1.1) + i * Inches(1.0)
    add_rect(sl, Inches(0.5), y, Inches(0.6), Inches(0.7), C_ACCENT)
    add_text(sl, num, Inches(0.5), y + Pt(6), Inches(0.6), Inches(0.65),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, label, Inches(1.3), y + Pt(6), Inches(10), Inches(0.65),
             size=22, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 4 — 直近の活動報告
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "直近の活動報告", 4)
footer_bar(sl)

bullets = [
    "就活終了（結果はまだ）",
    "長期インターン完全終了（全引き継ぎ完了）→ 研究に集中できる環境に",
    "",
    "研究作業（今回）:",
    "　参考論文 12 本をリポジトリに格納（research/papers/）",
    "　実験環境構築ガイドを作成（research/experiment-environment-setup.md）",
    "　API 予算見積もりを正確な実験設計ベースで更新",
    "",
    "余談：後期学費確保のため、スキマバイトの情報があればご教示ください🙏",
]
bullet_lines(sl, bullets, Inches(0.8), Inches(1.1), Inches(11.7), Inches(5.5), size=21)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 5 — 前回の振り返り（SCQA）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "前回の振り返り：研究テーマと承認済み方向性", 5)
footer_bar(sl)

scqa = [
    ("S  Situation",   "LLM は自信満々に誤った情報を生成する（ハルシネーション）"),
    ("C  Complication","英語では verbalized confidence が有効と判明。日本語は未検証の空白"),
    ("Q  Question",    "日本語環境でプロンプト設計によりキャリブレーションを改善できるか？"),
    ("A  Answer",      "前回承認：3手法 × 4モデル × 1,000問で検証する"),
]
colors = [C_GRAY, C_ACCENT2, C_ACCENT, C_GREEN]
for i, (label, body) in enumerate(scqa):
    y = Inches(1.1) + i * Inches(1.35)
    add_rect(sl, Inches(0.5), y, Inches(1.6), Inches(1.1), colors[i])
    add_text(sl, label, Inches(0.52), y + Pt(8), Inches(1.56), Inches(0.95),
             size=15, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, body, Inches(2.3), y + Pt(12), Inches(10.5), Inches(0.9),
             size=20, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 6 — 今回の進捗サマリー
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今回の進捗サマリー（4項目）", 6)
footer_bar(sl)

add_text(sl, "→ Slide 7〜10 で各項目を詳述",
         Inches(0.8), Inches(0.92), Inches(10), Inches(0.4),
         size=14, color=C_GRAY)

rows = [
    ("①", "評価指標", "ECE（主）＋ Brier Score（副）＋ AUROC（補助）に決定"),
    ("②", "データセット", "4ドメイン × 250問 = 計 1,000問 に確定"),
    ("③", "正答判定", "タスク別に最適手法を選定（翻訳のみ COMET 閾値）"),
    ("④", "プロンプト", "Verb.1S / Verb.2S / Ling.1S の 3条件を設計完了"),
]
for i, (no, item, result) in enumerate(rows):
    y = Inches(1.4) + i * Inches(1.3)
    add_rect(sl, Inches(0.4), y, Inches(0.55), Inches(1.0), C_ACCENT)
    add_text(sl, no, Inches(0.4), y + Pt(10), Inches(0.55), Inches(0.9),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(1.1), y, Inches(2.1), Inches(1.0), C_LIGHTBG)
    add_text(sl, item, Inches(1.15), y + Pt(10), Inches(2.0), Inches(0.9),
             size=20, bold=True, color=C_ACCENT)
    add_text(sl, result, Inches(3.4), y + Pt(10), Inches(9.6), Inches(0.9),
             size=19, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 7 — 進捗①：評価指標
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗①：評価指標の決定", 7)
footer_bar(sl)

metrics = [
    ("ECE\n（主指標）",    C_ACCENT,  "先行研究（Tian 2023, Xiong 2024）と直接比較可能\n10ビン等幅分割、低いほど良"),
    ("Brier Score\n（副指標）", C_ACCENT2, "理論的保証あり（Proper Scoring Rule）\nMurphy 分解で誤差と識別能力を分離"),
    ("AUROC\n（補助指標）", C_GREEN,   "ECE と直交する識別能力を独立評価\nXiong 2024 と同一指標"),
]
for i, (name, color, desc) in enumerate(metrics):
    x = Inches(0.4) + i * Inches(4.3)
    add_rect(sl, x, Inches(1.1), Inches(4.0), Inches(0.85), color)
    add_text(sl, name, x, Inches(1.12), Inches(4.0), Inches(0.82),
             size=20, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, x, Inches(2.0), Inches(4.0), Inches(3.5), C_LIGHTBG)
    add_text(sl, desc, x + Inches(0.1), Inches(2.1), Inches(3.8), Inches(3.3),
             size=18, color=C_DARK)

add_text(sl, "可視化: Reliability Diagram（論文 Figure に必ず掲載）",
         Inches(0.6), Inches(5.8), Inches(12), Inches(0.5),
         size=17, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 8 — 進捗②：データセット
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗②：使用データセットの選定", 8)
footer_bar(sl)

datasets = [
    ("数学", "MGSM", "GSM8K の日本語版", "正規化完全一致"),
    ("常識", "JCommonsenseQA", "5択 MC", "選択肢ラベル一致"),
    ("知識", "JMMLU", "日本史中心4科目", "選択肢ラベル一致"),
    ("翻訳", "FLORES-200", "日英対訳ペア", "COMET スコア閾値"),
]
add_text(sl, "各 250 問 × 4 ドメイン = 合計 1,000 問",
         Inches(0.6), Inches(0.92), Inches(12), Inches(0.45),
         size=20, bold=True, color=C_ACCENT)

for i, (domain, name, desc, judge) in enumerate(datasets):
    y = Inches(1.45) + i * Inches(1.25)
    add_rect(sl, Inches(0.4), y, Inches(1.5), Inches(1.05), C_ACCENT)
    add_text(sl, domain, Inches(0.4), y + Pt(6), Inches(1.5), Inches(0.95),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, name, Inches(2.1), y + Pt(6), Inches(3.2), Inches(0.45),
             size=20, bold=True, color=C_DARK)
    add_text(sl, desc, Inches(2.1), y + Pt(30), Inches(3.2), Inches(0.5),
             size=16, color=C_GRAY)
    add_text(sl, f"判定: {judge}", Inches(5.5), y + Pt(10), Inches(7.5), Inches(0.85),
             size=18, color=C_DARK)

add_text(sl, "旧計画: 25問/ドメイン → 250問/ドメインに変更（ECE統計的信頼性のため）",
         Inches(0.5), Inches(6.6), Inches(12), Inches(0.45),
         size=16, color=C_ACCENT2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 9 — 進捗③：正答判定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗③：正答判定方法の確立", 9)
footer_bar(sl)

rows = [
    ("数学", "正規化完全一致（数値抽出）"),
    ("常識・知識", "選択肢ラベル一致"),
    ("翻訳", "COMET スコア閾値（人間 50 文で F1 最適化）"),
]
for i, (domain, method) in enumerate(rows):
    y = Inches(1.1) + i * Inches(1.15)
    add_rect(sl, Inches(0.4), y, Inches(2.2), Inches(0.9), C_LIGHTBG)
    add_text(sl, domain, Inches(0.45), y + Pt(8), Inches(2.1), Inches(0.8),
             size=20, bold=True, color=C_ACCENT)
    add_text(sl, method, Inches(2.8), y + Pt(8), Inches(10.1), Inches(0.8),
             size=20, color=C_DARK)

add_rect(sl, Inches(0.4), Inches(4.55), W - Inches(0.8), Inches(1.8), C_LIGHTBG)
add_text(sl, "翻訳に LLM-as-a-Judge を主判定に使わない理由（Zheng et al. 2023）",
         Inches(0.6), Inches(4.6), Inches(12), Inches(0.5),
         size=18, bold=True, color=C_ACCENT2)
add_text(sl, "位置バイアス / 多数決コスト増大 / 再現性の問題\n→ 境界サンプルの検証手段としてのみ使用",
         Inches(0.7), Inches(5.15), Inches(12), Inches(1.0),
         size=17, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 10 — 進捗④：プロンプト設計
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "進捗④：プロンプトの設計", 10)
footer_bar(sl)

conds = [
    ("Verb.1S", "回答 + 確信度を同時出力\n（0.0〜1.0）", "Xiong 2024\nVanilla"),
    ("Verb.2S", "Turn1: 回答\nTurn2: 確信度を質問\n（2コール/問）", "Tian 2023\nTwo-Stage"),
    ("Ling.1S", "「ほぼ確実」等の\n言語表現→数値マッピング", "Tian 2023\nLinguistic"),
]
for i, (name, desc, ref) in enumerate(conds):
    x = Inches(0.4) + i * Inches(4.3)
    add_rect(sl, x, Inches(1.05), Inches(4.0), Inches(0.75), C_ACCENT)
    add_text(sl, name, x, Inches(1.07), Inches(4.0), Inches(0.72),
             size=24, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, x, Inches(1.85), Inches(4.0), Inches(3.0), C_LIGHTBG)
    add_text(sl, desc, x + Inches(0.1), Inches(1.95), Inches(3.8), Inches(2.8),
             size=18, color=C_DARK)
    add_text(sl, f"対応先行研究:\n{ref}", x + Inches(0.1), Inches(4.9), Inches(3.8), Inches(1.0),
             size=15, color=C_GRAY)

add_text(sl,
         "CoT を独立条件にしない理由：正答率自体を変化させ確信度設計の効果と分離困難\n"
         "全ドメイン × 日英のテンプレートを確定済み",
         Inches(0.5), Inches(6.1), Inches(12.5), Inches(0.9),
         size=16, color=C_ACCENT2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 11 — 実験環境構築
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "次のフェーズへの移行：実験環境構築", 11)
footer_bar(sl)

add_text(sl, "整備済み", Inches(0.5), Inches(1.0), Inches(3), Inches(0.5),
         size=18, bold=True, color=C_GREEN)
done = [
    "✅  参考論文 PDF 12 本をリポジトリに格納（research/papers/）",
    "✅  必要ツール・インストール手順をドキュメント化（experiment-environment-setup.md）",
]
bullet_lines(sl, done, Inches(0.7), Inches(1.5), Inches(12), Inches(1.2), size=19)

tools = [
    ("ECE 計算",     "netcal",                    "Xiong 2024 採用実績"),
    ("AUROC / Brier", "scikit-learn",             "roc_auc_score / brier_score_loss"),
    ("GPT API",      "openai==1.43.0",            "全4論文で使用"),
    ("Claude API",   "anthropic==0.33.0",         "Tian 2023 で使用"),
    ("Gemini API",   "google-generativeai",       "本研究で新規追加"),
    ("データセット", "datasets (HuggingFace)",    "MGSM / JMMLU / FLORES-200"),
    ("翻訳評価",     "unbabel-comet",             "FLORES-200 ドメイン用"),
]
add_text(sl, "主要ツール一覧", Inches(0.5), Inches(2.85), Inches(3), Inches(0.45),
         size=17, bold=True, color=C_ACCENT)
for i, (cat, tool, note) in enumerate(tools):
    y = Inches(3.35) + i * Inches(0.52)
    add_text(sl, cat,  Inches(0.6),  y, Inches(2.3), Inches(0.48), size=15, color=C_GRAY)
    add_text(sl, tool, Inches(3.0),  y, Inches(3.5), Inches(0.48), size=15, bold=True, color=C_ACCENT)
    add_text(sl, note, Inches(6.6),  y, Inches(6.4), Inches(0.48), size=15, color=C_DARK)

add_text(sl, "次のステップ：Python スクリプト実装（7月中旬・中間発表前に完了目標）",
         Inches(0.5), Inches(7.1), Inches(12), Inches(0.4),
         size=16, bold=True, color=C_ACCENT2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 12 — 今後の方向性サマリー
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の方向性サマリー", 12)
footer_bar(sl)

summary = [
    ("着地地点", "A〜D の複数シナリオを用意済み（秦野先生ご指摘への対応）"),
    ("予算",    "約 3,000 円（研究室枠 50,000 円の 6% 以内）"),
    ("次の山場", "7月17日 概要2p提出 → 7月20〜27日 中間発表"),
]
for i, (label, body) in enumerate(summary):
    y = Inches(1.3) + i * Inches(1.7)
    add_rect(sl, Inches(0.4), y, Inches(2.2), Inches(1.3), C_ACCENT)
    add_text(sl, label, Inches(0.4), y + Pt(12), Inches(2.2), Inches(1.1),
             size=22, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, body, Inches(2.9), y + Pt(16), Inches(10.0), Inches(1.1),
             size=21, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 13 — 着地地点の複数構想
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "着地地点の複数構想（秦野先生ご指摘への回答）", 13)
footer_bar(sl)

add_text(sl, "ご指摘：「ライバルが出てきそうなので着地地点を複数用意すべき」",
         Inches(0.5), Inches(0.92), Inches(12), Inches(0.5),
         size=17, color=C_GRAY)

plans = [
    ("A（本命）",  C_GREEN,    "予定通り進捗", "日本語 × 複数モデル × 3手法の全比較"),
    ("B",          C_ACCENT,   "差が有意でない", "ネガティブ結果の体系的報告（それ自体が学術貢献）"),
    ("C",          C_ACCENT2,  "競合研究が先行", "翻訳ドメインに絞り込んで深掘り（COMET × 確信度）"),
    ("D",          C_GRAY,     "11月末時間不足", "スコープ縮小トリガー発動（文書化済み）"),
]
for i, (name, color, cond, content) in enumerate(plans):
    y = Inches(1.55) + i * Inches(1.3)
    add_rect(sl, Inches(0.4), y, Inches(1.4), Inches(1.1), color)
    add_text(sl, name, Inches(0.4), y + Pt(8), Inches(1.4), Inches(0.95),
             size=18, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_rect(sl, Inches(1.95), y, Inches(2.5), Inches(1.1), C_LIGHTBG)
    add_text(sl, cond, Inches(2.0), y + Pt(10), Inches(2.4), Inches(0.9),
             size=16, color=C_GRAY)
    add_text(sl, content, Inches(4.6), y + Pt(10), Inches(8.6), Inches(0.9),
             size=19, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 14 — 予算見積もり
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "予算見積もり（確定版）", 14)
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(1.0), W - Inches(0.8), Inches(0.75), C_LIGHTBG)
add_text(sl, "実験全体の合計：約 $20 USD ≈ 3,000 円（×2倍バッファ込み）　←　研究室枠 50,000 円の 6%",
         Inches(0.6), Inches(1.05), Inches(12.5), Inches(0.65),
         size=20, bold=True, color=C_ACCENT)

models = [
    ("Claude Sonnet 4.6", "$3.00", "$15.00"),
    ("GPT-4o",            "$2.50", "$10.00"),
    ("GPT-5",             "$0.63", "$5.00"),
    ("Gemini 2.0 Flash",  "$0.15", "$0.60"),
]
add_text(sl, "モデル", Inches(0.5), Inches(1.95), Inches(4), Inches(0.45),
         size=16, bold=True, color=C_GRAY)
add_text(sl, "入力 $/1M トークン", Inches(4.6), Inches(1.95), Inches(3.5), Inches(0.45),
         size=16, bold=True, color=C_GRAY)
add_text(sl, "出力 $/1M トークン", Inches(8.4), Inches(1.95), Inches(4), Inches(0.45),
         size=16, bold=True, color=C_GRAY)

for i, (model, inp, out) in enumerate(models):
    y = Inches(2.45) + i * Inches(0.75)
    bg = C_LIGHTBG if i % 2 == 0 else C_BG
    add_rect(sl, Inches(0.4), y, W - Inches(0.8), Inches(0.72), bg)
    add_text(sl, model, Inches(0.55), y + Pt(6), Inches(4.2), Inches(0.62), size=19, color=C_DARK)
    add_text(sl, inp,   Inches(4.9),  y + Pt(6), Inches(3.2), Inches(0.62), size=19, color=C_DARK)
    add_text(sl, out,   Inches(8.6),  y + Pt(6), Inches(3.5), Inches(0.62), size=19, color=C_DARK)

add_text(sl, "オープンソースモデル（Swallow・ELYZA・Qwen）はローカル実行 → 追加費用なし",
         Inches(0.5), Inches(5.7), Inches(12.5), Inches(0.45),
         size=16, color=C_GRAY)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 15 — スケジュール
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後のスケジュール", 15)
footer_bar(sl)

schedule = [
    ("6月（残り）",     C_ACCENT,   "実験スクリプト実装・パイロット実験（動作確認）"),
    ("7月 17日 ⚠️",     C_ACCENT2,  "中間発表 概要 2p PDF 提出（LETUS 12:00 厳守）"),
    ("7月 20〜27日 ⚠️", C_ACCENT2,  "中間発表会（6分＋質疑3分）"),
    ("8〜9月",          C_ACCENT,   "本実験（4ドメイン × 4モデル × 3プロンプト方式）"),
    ("10月",            C_ACCENT,   "結果分析・統計検定・考察"),
    ("11月〜1月",       C_ACCENT,   "論文執筆・提出"),
]
for i, (period, color, task) in enumerate(schedule):
    y = Inches(1.1) + i * Inches(1.0)
    add_rect(sl, Inches(0.4), y, Inches(2.2), Inches(0.85), color)
    add_text(sl, period, Inches(0.4), y + Pt(6), Inches(2.2), Inches(0.78),
             size=17, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
    add_text(sl, task, Inches(2.8), y + Pt(10), Inches(10.1), Inches(0.75),
             size=19, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Slide 16 — 参考文献
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "参考文献", 16)
footer_bar(sl)

refs = [
    "Guo et al. (2017) ICML — On Calibration of Modern Neural Networks",
    "Kadavath et al. (2022) arXiv — Language Models (Mostly) Know What They Know",
    "Tian et al. (2023) EMNLP — Just Ask for Calibration",
    "Xiong et al. (2024) ICLR — Can LLMs Express Their Uncertainty?",
    "Zheng et al. (2023) NeurIPS — Judging LLM-as-a-Judge",
    "Yang et al. (2024) arXiv:2412.14737 — On Verbalized Confidence Scores for LLMs",
    "Xue et al. (2025) ACL Findings — MlingConf",
    "Seo et al. (2025) arXiv:2510.10913 — ADVICE",
    "Li, Xiong, Wu, Hooi (2025) arXiv:2508.18847 — ConfTuner",
]
bullet_lines(sl, refs, Inches(0.6), Inches(1.1), Inches(12.5), Inches(6.0), size=17)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Appendix A — ECE 数式
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Appendix A：ECE 数式", 17)
footer_bar(sl)

add_rect(sl, Inches(1.5), Inches(1.4), Inches(10.3), Inches(2.0), C_LIGHTBG)
add_text(sl,
         "ECE = Σ_{m=1}^{M}  (|B_m| / n)  ×  |acc(B_m) − conf(B_m)|",
         Inches(1.7), Inches(1.55), Inches(10.0), Inches(1.6),
         size=26, bold=True, color=C_DARK, align=PP_ALIGN.CENTER)

defs = [
    "B_m  : ビン m に属するサンプル集合",
    "acc  : ビン内の正答率",
    "conf : ビン内の平均確信度",
    "M = 10、等幅ビン [0, 1] を 0.1 刻みで分割",
    "n    : サンプル総数",
]
bullet_lines(sl, defs, Inches(1.8), Inches(3.6), Inches(10), Inches(3.0), size=20)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Appendix B — プロンプトテンプレート
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Appendix B：プロンプトテンプレート（Verb.1S 例）", 18)
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(1.05), W - Inches(0.8), Inches(5.8), C_LIGHTBG)
add_text(sl,
         "以下の数学の問題を読み、回答と、その回答が正しいと思う確率（確信度）を\n"
         "答えてください。確信度は 0.0（まったく自信がない）から 1.0（完全に確信\n"
         "している）の数値で表してください。\n\n"
         "問題: {question}\n\n"
         "以下の形式で回答してください。形式以外の出力はしないでください。\n"
         "回答: [数値のみ]\n"
         "確信度: [0.0〜1.0の数値]",
         Inches(0.7), Inches(1.2), Inches(11.9), Inches(5.5),
         size=18, color=C_DARK)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Appendix C — 実験計画全体像
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Appendix C：実験計画の全体像", 19)
footer_bar(sl)

rows = [
    ("実験①", "基本キャリブレーション", "4モデル × 4ドメイン × Verb.1S", "4,000"),
    ("実験②", "プロンプト手法比較",      "1モデル × Verb.2S + Ling.1S",  "3,000"),
    ("実験③", "日英比較",                "1モデル × 英語版 1,000問",      "1,000"),
    ("合計",   "×2倍バッファ込み",       "",                               "~16,000"),
]
headers = ["実験", "目的", "条件", "コール数"]
col_w = [Inches(1.4), Inches(4.0), Inches(5.5), Inches(1.9)]
col_x = [Inches(0.4), Inches(1.9), Inches(6.0), Inches(11.6)]

for j, (h, w, x) in enumerate(zip(headers, col_w, col_x)):
    add_rect(sl, x, Inches(1.05), w, Inches(0.6), C_ACCENT)
    add_text(sl, h, x, Inches(1.07), w, Inches(0.56),
             size=17, bold=True, color=C_BG, align=PP_ALIGN.CENTER)

for i, row in enumerate(rows):
    y = Inches(1.7) + i * Inches(1.2)
    bg = C_LIGHTBG if i % 2 == 0 else C_BG
    if i == len(rows) - 1:
        bg = RGBColor(0xFF, 0xF0, 0xE0)
    for j, (cell, w, x) in enumerate(zip(row, col_w, col_x)):
        add_rect(sl, x, y, w, Inches(1.1), bg)
        add_text(sl, cell, x + Inches(0.05), y + Pt(8), w - Inches(0.1), Inches(0.95),
                 size=17, color=C_DARK, align=PP_ALIGN.CENTER if j in [0, 3] else PP_ALIGN.LEFT)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 保存
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT = "2026-06-24-seminar-slides.pptx"
prs.save(OUTPUT)
print(f"✅  {OUTPUT} を生成しました（{prs.slides.__len__()} スライド）")
