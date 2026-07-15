"""
説明用資料（兼・内容理解を深めるための資料）スライド生成スクリプト
python generate_slides_full_explainer.py で .pptx を生成

位置づけ: research/midterm-presentation/abstract/abstract_full_v1.tex の内容を
そのままスライド化したもの。6分の中間発表用デッキ（midterm-presentation-slides.pptx）
とは別物であり，1スライド1メッセージのルールは緩め，情報密度を優先する。
教授への説明資料，および本人の内容理解を深めるための参照資料として使うことを想定。

デザイン方針:
  - 情報密度優先のため箇条書き3項目までの制限は適用しない
  - フォントは可読性を保つため18pt以上とする（発表用ほど厳格な最低値は設けない）
  - グレー文字・"⇔"は引き続き使用しない
  - 比較情報は表で表現する
  - 数式はpptxでTeXを直接レンダリングできないため，Unicode近似表記で記載する
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

C_BG      = RGBColor(0xFF, 0xFF, 0xFF)
C_ACCENT  = RGBColor(0x1A, 0x56, 0xAA)
C_ACCENT2 = RGBColor(0xB0, 0x2A, 0x1E)
C_DARK    = RGBColor(0x14, 0x14, 0x1E)
C_LIGHTBG = RGBColor(0xEC, 0xF1, 0xF9)
C_GAPBG   = RGBColor(0xFB, 0xEC, 0xEA)
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

W = Inches(13.33)
H = Inches(7.5)

prs = Presentation()
prs.slide_width = W
prs.slide_height = H
BLANK = prs.slide_layouts[6]

TOTAL_SLIDES = 34


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


def add_text(slide, text, x, y, w, h, size=20, bold=False, color=C_DARK,
             align=PP_ALIGN.LEFT, wrap=True, italic=False, anchor=None, font="Meiryo"):
    assert size >= 16, "可読性のため16pt未満は避ける（解説資料のため発表用の18pt制限は緩和）"
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


def bullet_box(slide, lines, x, y, w, h, size=20, color=C_DARK, spacing=8, level_map=None):
    """解説資料のため箇条書き数の制限は設けない（発表用ルールとは別扱い）"""
    assert size >= 16, "可読性のため16pt未満は避ける（解説資料のため発表用の18pt制限は緩和）"
    txBox = slide.shapes.add_textbox(x, y, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if i > 0 else tf.paragraphs[0]
        if level_map and i in level_map:
            p.level = level_map[i]
        p.space_before = Pt(spacing)
        run = p.add_run()
        prefix = "　- " if (level_map and level_map.get(i)) else "・"
        run.text = f"{prefix}{line}"
        run.font.size = Pt(size)
        run.font.color.rgb = color


def add_table(slide, headers, rows, x, y, w, h, header_size=18, body_size=16):
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


def header_bar(slide, title_text, slide_no=None, subtitle=None, title_size=28):
    add_rect(slide, 0, 0, W, Inches(0.12), C_ACCENT)
    add_text(slide, title_text, Inches(0.5), Inches(0.28), Inches(11.3), Inches(0.7),
             size=title_size, bold=True, color=C_DARK)
    if subtitle:
        add_text(slide, subtitle, Inches(0.5), Inches(0.85), Inches(11.6), Inches(0.4),
                  size=18, italic=True, color=C_ACCENT)
    if slide_no:
        add_text(slide, f"{slide_no}/{TOTAL_SLIDES}", Inches(12.0), Inches(0.28),
                  Inches(1.1), Inches(0.5), size=18, color=C_ACCENT, align=PP_ALIGN.RIGHT)


def prior_work_slide(title, slide_no, content_lines, gap_lines, subtitle=None):
    sl = prs.slides.add_slide(BLANK)
    header_bar(sl, title, slide_no, subtitle=subtitle)
    add_text(sl, "先行研究の内容", Inches(0.6), Inches(1.4), Inches(11.7), Inches(0.45),
              size=20, bold=True, color=C_ACCENT)
    bullet_box(sl, content_lines, Inches(0.6), Inches(1.85), Inches(12.1), Inches(2.6),
               size=18, spacing=8)
    gap_y = Inches(4.55)
    add_rect(sl, Inches(0.5), gap_y, Inches(12.3), Inches(0.45 + 0.42 * len(gap_lines)), C_GAPBG)
    add_text(sl, "残された研究の余地", Inches(0.7), gap_y + Inches(0.1), Inches(11.7), Inches(0.4),
              size=20, bold=True, color=C_ACCENT2)
    bullet_box(sl, gap_lines, Inches(0.7), gap_y + Inches(0.55), Inches(11.9), Inches(1.6),
               size=18, spacing=6)
    return sl


# ══════════════════════════════════════════════════════════════
# 1. 表紙
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, C_ACCENT)
add_text(sl, "確信度プロンプト方式の比較による\nLLMキャリブレーション性能の検証",
         Inches(0.8), Inches(1.3), Inches(11.7), Inches(1.8),
         size=34, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "説明用資料（フル版）：abstract_full_v1.tex の内容を全て収録",
         Inches(0.8), Inches(3.0), Inches(11.7), Inches(0.6),
         size=20, italic=True, color=C_WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "グループE　秦野研究室　7422048　指田一茶",
         Inches(0.8), Inches(4.6), Inches(11.7), Inches(0.6),
         size=22, color=C_WHITE, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# 2. 目次
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "目次", 2)
bullet_box(sl, [
    "研究背景（ハルシネーション・キャリブレーション・先行研究3本・研究の論理チェーン）",
    "研究目的（主目的・付随目的・サブRQ）",
    "研究の方針（モデル・データセット・プロンプト全文・評価指標・仮説）",
    "現在の進捗",
    "今後の予定（スケジュール・Murphy分解・リスク）",
    "参考文献",
], Inches(0.8), Inches(1.7), Inches(11.5), Inches(4.5), size=22, spacing=16)


# ══════════════════════════════════════════════════════════════
# 3. 問題意識：ハルシネーションとキャリブレーション
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "問題意識：ハルシネーションとキャリブレーション", 3)
bullet_box(sl, [
    "LLMは教育・業務・日常生活へ急速に普及している",
    "「ハルシネーション」：誤情報を自信満々に生成する問題が未解決（Ji et al. 2023）",
    "問題の本質は「確信度」と「実際の正答率」の乖離にある",
    "確信度が正答率と一致していれば（well-calibrated），利用者はリスク判断の手がかりにできる",
    "この性質を「キャリブレーション（calibration）」と呼び，ECE等の指標で定量化する（Guo et al. 2017）",
], Inches(0.7), Inches(1.7), Inches(11.9), Inches(4.8), size=20, spacing=14)


# ══════════════════════════════════════════════════════════════
# 4. なぜプロンプト設計なのか
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "なぜプロンプト設計なのか：手法の全体マップ", 4)
add_table(sl,
          headers=["系統", "代表手法", "前提となるアクセス"],
          rows=[
              ["Post-hoc補正", "Temperature Scaling, Adaptive Temp. Scaling, Prior Adaptation", "内部logitsへのアクセス"],
              ["ファインチューニング", "Calibration-Aware FT, ConfTuner", "モデルパラメータへのアクセス"],
              ["プロンプト設計", "Verbalized Confidence", "不要（プロンプトのみ）"],
          ],
          x=Inches(0.6), y=Inches(1.5), w=Inches(12.1), h=Inches(2.2), header_size=18, body_size=16)
bullet_box(sl, [
    "GPT-4o・Claude・GeminiのようなAPIはlogits・パラメータへのアクセスを提供しない",
    "Xie et al. 2024（Black-Box Calibration Survey）はこの制約を専用サーベイが必要なほど本質的と指摘",
    "→ 一般利用者が商用APIに今すぐ適用できる手段はプロンプト設計のみ",
], Inches(0.7), Inches(4.0), Inches(11.9), Inches(2.2), size=20, spacing=12)


# ══════════════════════════════════════════════════════════════
# 5. 先行研究1: Tian 2023
# ══════════════════════════════════════════════════════════════
prior_work_slide(
    "先行研究1：Tian et al. 2023「Just Ask for Calibration」", 5,
    subtitle="EMNLP 2023",
    content_lines=[
        "RQ: プロンプトだけで確信度を引き出した場合，内部確率より良い較正が得られるか",
        "GPT-3.5/GPT-4/LLaMA-2-Chat等，TriviaQA・SciQ・TruthfulQA等で検証",
        "4方式を比較：logprob／linguistic／verbal numeric／top-k（複数候補同時提示）",
        "結果：RLHF後はlogprobベースの較正が崩壊するが，verbalized confidenceは良好",
        "特にtop-k方式（複数候補同時提示）が最も良好。ECEを約50%削減",
    ],
    gap_lines=[
        "検証は英語のQAタスクのみ。日本語モデル・タスクでの再現性は未検証",
        "top-k方式はAPI呼び出しコストが増大するため，本研究では不採用",
    ],
)


# ══════════════════════════════════════════════════════════════
# 6. Tian 2023の4方式比較表 + RLHFの影響
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "補足：Tian 2023 の4方式とRLHFの影響", 6)
add_table(sl,
          headers=["方式", "内容", "傾向"],
          rows=[
              ["logprob", "内部確率をそのまま使う", "RLHF後は較正が崩壊"],
              ["linguistic", "「どれくらい自信があるか」と言葉で聞く", "logprobより良好"],
              ["verbal numeric", "0-100の数値で答えさせる", "最も良好な部類"],
              ["top-k", "複数候補と各確率を同時提示", "さらに良好（本研究は不採用）"],
          ],
          x=Inches(0.6), y=Inches(1.5), w=Inches(12.1), h=Inches(2.4), header_size=18, body_size=16)
bullet_box(sl, [
    "Figure 2（Tian 2023）：Llama-70Bで，RLHF適用前後のlogprobベース較正（ECE/AUC）を比較",
    "→ RLHF適用後はTriviaQA・SciQ・TruthfulQAのいずれでも較正が悪化することを実験で確認",
    "この発見が「なぜverbalized confidenceを使うのか」の直接的な根拠になっている",
], Inches(0.7), Inches(4.1), Inches(11.9), Inches(2.2), size=18, spacing=10)


# ══════════════════════════════════════════════════════════════
# 7. 先行研究2: Xiong 2024
# ══════════════════════════════════════════════════════════════
prior_work_slide(
    "先行研究2：Xiong et al. 2024「Can LLMs Express Their Uncertainty?」", 7,
    subtitle="ICLR 2024",
    content_lines=[
        "Black-box確信度推定の体系的フレームワークを提案",
        "3要素：プロンプト戦略／サンプリング方法（複数回応答）／集約手法（一貫性計算）",
        "5種類のデータセット×5モデル（GPT-4，LLaMA-2等）でキャリブレーションと失敗予測を評価",
        "発見：LLMは総じて過信しがち。モデルが強いほど改善するが理想には遠い",
        "どの方式も一貫して他を上回らない。white-boxとの差はわずか（AUROC 0.522→0.605）",
    ],
    gap_lines=[
        "専門知識を要するタスクでは全手法が苦戦しており，著者ら自身が改善の余地を指摘",
        "検証は英語中心で，日本語での体系的な方式間比較は行っていない",
    ],
)


# ══════════════════════════════════════════════════════════════
# 8. 先行研究3: MlingConf（内容）
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "先行研究3：MlingConf（Xue et al. 2025）", 8, subtitle="Findings of ACL 2025")
bullet_box(sl, [
    "英語・日本語・中国語・フランス語・タイ語の5言語でLLMの確信度推定を検証",
    "確信度手法：Prob.（トークン確率）／p(True)／Verb.（0-100の数値，単一手法）の3種を比較",
    "Language-Agnostic（TriviaQA/GSM8K/CommonsenseQA/SciQ）と Language-Specific（LSQA）の2種のタスク",
    "日本語データセットは英語から機械翻訳（50サンプルの人手評価で翻訳正解率96〜98%）",
], Inches(0.7), Inches(1.6), Inches(11.9), Inches(2.6), size=19, spacing=12)
add_rect(sl, Inches(0.5), Inches(4.4), Inches(12.3), Inches(2.3), C_LIGHTBG)
bullet_box(sl, [
    "発見①：モデルの指示追従能力によって最適な手法が変わる（GPT-3.5はp(True)/Verb.，Llama-3.1はProb.）",
    "発見②：日本語では複数のLAタスクでECEが英語より悪化する傾向（例：TriviaQA・GPT-3.5で英16.52 vs 日34.49）",
    "発見③：質問と同じ言語でプロンプトする「Native-Tone Prompting」で言語固有タスクの精度が改善",
], Inches(0.7), Inches(4.55), Inches(11.9), Inches(2.1), size=18, spacing=10)


# ══════════════════════════════════════════════════════════════
# 9. MlingConfの限界と比較表
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "MlingConfの限界と先行研究全体の比較", 9)
add_table(sl,
          headers=["", "Tian/Xiong (英語)", "MlingConf (多言語)", "本研究"],
          rows=[
              ["対象言語", "英語のみ", "日本語含む5言語", "日本語"],
              ["方式間の比較", "なし", "なし（単一手法）", "あり（3方式）"],
              ["データセット", "英語標準", "英語からの機械翻訳", "日本語ネイティブ＋標準"],
              ["検証モデル", "GPT系(当時)", "GPT-3.5・Llama-3.1", "現行世代モデル"],
          ],
          x=Inches(0.6), y=Inches(1.5), w=Inches(12.1), h=Inches(2.6), header_size=18, body_size=16)
bullet_box(sl, [
    "新規性の主張は「日本語検証が皆無」ではなく「十分に研究されていない」という限定的で反証可能な形にする",
    "本研究が埋めるのは表の太字3点：方式間比較・日本語ネイティブデータセット・現行世代モデル",
], Inches(0.7), Inches(4.4), Inches(11.9), Inches(1.8), size=19, spacing=12)


# ══════════════════════════════════════════════════════════════
# 10. 研究の論理的な繋がり (1/2)
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究の論理的な繋がり（一歩ずつの接続）(1/2)", 10)
add_table(sl,
          headers=["ステップ", "内容", "根拠文献"],
          rows=[
              ["① 較正の基礎指標", "ECEがLLMの信頼性を測る標準指標として確立", "Guo et al. 2017"],
              ["② 自己評価能力", "LLMは内部的に「知っているかどうか」の情報を持つ", "Kadavath et al. 2022"],
              ["③ 言語化の方法", "確信度を自然言語・数値でプロンプトから引き出す方式の定義", "Lin et al. 2022"],
              ["④ 英語での有効性", "ただ確信度を聞くだけで内部確率より良い較正（ECE約50%改善）", "Tian 2023; Xiong 2024"],
              ["⑤ 多言語での粗い検証", "日本語含む5言語で単一手法を検証。機械翻訳・単一手法のみ", "MlingConf (Xue 2025)"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(4.8), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 11. 研究の論理的な繋がり (2/2)
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究の論理的な繋がり（一歩ずつの接続）(2/2)", 11)
add_table(sl,
          headers=["ステップ", "内容", "根拠文献"],
          rows=[
              ["⑥ 聞き方への依存性", "プロンプトスタイルが較正結果に影響する", "Xia et al. 2025"],
              ["⑦ 数値表現の設計", "0-100は丸め値に偏る，0-20の方がメタ認知精度が良い", "Dai 2025"],
              ["⑧ 回答接地の効果", "確信度の回答非依存性が過信の主因（診断的知見）", "Seo et al. 2025 (ADVICE)"],
              ["⑨ アクセス制約", "logits/パラメータ非公開のためプロンプト設計のみ実行可能", "Xie et al. 2024"],
              ["⑩ 本研究の位置", "日本語ネイティブデータセットで3方式の差・現行モデル再現性を検証", "本研究のRQ0〜RQ4"],
              ["（オプション）⑪", "Brier ScoreをREL/RESに分離する視点も存在（探索的オプション）", "Bröcker 2009; Pohle 2020"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(5.0), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 12. 研究目的：主目的とメインRQ
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究目的：主たる目的とメインRQ", 12)
add_rect(sl, Inches(0.6), Inches(1.7), Inches(12.1), Inches(2.3), C_LIGHTBG)
add_text(sl, "主たる目的", Inches(0.85), Inches(1.85), Inches(11.6), Inches(0.5),
          size=22, bold=True, color=C_ACCENT)
add_text(sl,
         "日本語ネイティブなタスクにおいて確信度プロンプト方式（Verb.1S/Verb.2S/Ling.1S）の\n"
         "違いがキャリブレーション性能にどのような差をもたらすかを実証的に検証する",
         Inches(0.85), Inches(2.35), Inches(11.6), Inches(1.5), size=20, color=C_DARK)
add_text(sl,
         "このRQは実験結果からYES/NOで判定可能な形になっている点が重要である。\n"
         "方式間に有意差が「ある」か「ない」かのいずれの結果も報告可能な学術的知見になる。",
         Inches(0.7), Inches(4.3), Inches(11.9), Inches(1.5), size=19, italic=True, color=C_DARK)


# ══════════════════════════════════════════════════════════════
# 13. 付随目的・サブRQ・演習2との違い
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "付随目的・サブRQ・演習2との違い", 13)
add_text(sl, "付随して明らかになること：その効果は現行世代の商用LLMでも再現されるか？",
          Inches(0.7), Inches(1.5), Inches(11.9), Inches(0.6), size=20, bold=True, color=C_ACCENT2)
bullet_box(sl, [
    "サブRQ1：モデル間でキャリブレーション性能・改善パターンに差はあるか",
    "サブRQ2：タスクドメインによって改善幅は変化するか",
    "サブRQ4：日本語と英語で改善幅に差はあるか（英語側は既存文献の数値と比較，本研究内での再実験ではない）",
], Inches(0.7), Inches(2.3), Inches(11.9), Inches(2.2), size=19, spacing=10)
add_rect(sl, Inches(0.5), Inches(4.7), Inches(12.3), Inches(1.9), C_LIGHTBG)
add_text(sl,
         "演習2との違い：演習2は英語中心・少数プロンプトでの予備的なECE比較にとどまっていたが，\n"
         "本研究は日本語4ドメイン・3方式・複数モデルでの体系的検証へと発展させるものであり，\n"
         "演習2の焼き直しではなく，今後の本実験・考察へ直結する。",
         Inches(0.7), Inches(4.85), Inches(11.9), Inches(1.6), size=19, color=C_DARK)


# ══════════════════════════════════════════════════════════════
# 14. 方針：実験の全体像
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究の方針：実験の全体像", 14)
add_table(sl,
          headers=["実験", "目的", "扱う変数"],
          rows=[
              ["実験1", "基本キャリブレーションの測定", "モデル × ドメイン"],
              ["実験2", "プロンプト方式の影響", "プロンプトフォーマット"],
              ["実験3", "言語の影響（先行研究数値との比較）", "日本語 vs 英語"],
          ],
          x=Inches(1.0), y=Inches(1.8), w=Inches(11.3), h=Inches(2.3), header_size=19, body_size=18)
bullet_box(sl, [
    "各ドメイン250問，合計1,000問を使用",
    "ECE（10ビン）で各ビン平均25問を確保するための最低ラインとして設定（Roelofs et al. 2022）",
], Inches(0.7), Inches(4.4), Inches(11.9), Inches(1.6), size=19, spacing=10)


# ══════════════════════════════════════════════════════════════
# 15. 方針：使用モデル
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究の方針：使用モデル", 15)
bullet_box(sl, [
    "商用：GPT-4o / GPT-5，Claude Sonnet 4.6，Gemini 2.x",
    "オープン：Swallow，ELYZA-japanese-Llama，Qwen（バックアップ候補）",
    "合計4〜6モデルを予定",
    "モデルの正確なバージョン・取得日時は実験実施時に必ず記録し，再現性を担保する",
    "オープンソースモデルはローカル実行またはHugging Face無料枠を使用（追加コストなし）",
], Inches(0.7), Inches(1.8), Inches(11.9), Inches(4.5), size=21, spacing=16)


# ══════════════════════════════════════════════════════════════
# 16. 方針：データセット
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "研究の方針：データセット", 16)
add_table(sl,
          headers=["ドメイン", "データセット", "問数", "正答判定"],
          rows=[
              ["数学", "MGSM（日本語版GSM8K）", "250", "正規化完全一致"],
              ["常識", "JCommonsenseQA", "250", "選択肢ラベル一致"],
              ["知識", "JMMLU（公民・地理・慣用句、歴史は除外）", "250", "選択肢ラベル一致"],
              ["翻訳", "FLORES-200（日英ペア）", "250", "COMET閾値+LLM-as-a-Judge"],
          ],
          x=Inches(0.7), y=Inches(1.6), w=Inches(11.9), h=Inches(2.6), header_size=18, body_size=17)
bullet_box(sl, [
    "JCommonsenseQA・JMMLUは日本語話者向けに作成されたデータセット",
    "MGSM・FLORES-200は多言語比較で標準的に用いられるベンチマーク（多言語展開/対訳コーパス）",
], Inches(0.7), Inches(4.5), Inches(11.9), Inches(1.6), size=18, spacing=10)


# ══════════════════════════════════════════════════════════════
# 17. 方針：Verb.1Sのプロンプト全文
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "プロンプト方式①：Verb.1S（同時出力）", 17)
add_rect(sl, Inches(0.7), Inches(1.6), Inches(11.9), Inches(2.6), C_LIGHTBG)
add_text(sl,
         "以下の数学の問題を読み，回答と，その回答が正しいと思う確率（確信度）を答えてください。\n"
         "確信度は0.0（まったく自信がない）から1.0（完全に確信している）の数値で表してください。\n\n"
         "問題: {question}\n\n"
         "回答: [数値のみ]\n確信度: [0.0〜1.0の数値]",
         Inches(0.9), Inches(1.75), Inches(11.5), Inches(2.4), size=17, color=C_DARK)
bullet_box(sl, [
    "Xiong 2024のVanilla方式に対応。回答と確信度を1回のやり取りで同時出力させる",
    "常識QA・知識QA・翻訳ドメインでは回答形式指示部分のみドメイン固有の内容に置換",
], Inches(0.7), Inches(4.5), Inches(11.9), Inches(1.6), size=19, spacing=10)


# ══════════════════════════════════════════════════════════════
# 18. 方針：Verb.2Sのプロンプト全文
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "プロンプト方式②：Verb.2S（別ターンで質問）", 18)
add_rect(sl, Inches(0.7), Inches(1.5), Inches(11.9), Inches(3.0), C_LIGHTBG)
add_text(sl,
         "[Turn 1] 以下の数学の問題に回答してください。\n"
         "問題: {question}　→　回答: [数値のみ]\n\n"
         "[Turn 2] あなたは先ほどの問題に対して「{answer}」と回答しました。\n"
         "この回答が正しい確率を0.0〜1.0の数値で答えてください。\n"
         "確信度: [0.0〜1.0の数値]",
         Inches(0.9), Inches(1.65), Inches(11.5), Inches(2.8), size=17, color=C_DARK)
bullet_box(sl, [
    "Xiong 2024のSelf-Probing／Tian 2023のTwo-Stageに対応",
    "回答と確信度評価を分離することで回答依存型の確信度を誘発（ADVICEの診断的知見を踏まえた設計）",
], Inches(0.7), Inches(4.7), Inches(11.9), Inches(1.6), size=19, spacing=10)


# ══════════════════════════════════════════════════════════════
# 19. 方針：Ling.1Sのプロンプト全文とマッピング
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "プロンプト方式③：Ling.1S（言語表現）", 19)
add_table(sl,
          headers=["言語表現", "数値"],
          rows=[
              ["ほぼ確実", "0.95"], ["かなり自信がある", "0.80"],
              ["どちらともいえない", "0.50"], ["あまり自信がない", "0.25"],
              ["ほとんどわからない", "0.05"],
          ],
          x=Inches(1.5), y=Inches(1.6), w=Inches(10.3), h=Inches(3.0), header_size=18, body_size=17)
bullet_box(sl, [
    "Tian 2023のLinguistic方式に対応。マッピングはTianのアンカーを踏襲",
    "対応表の設定自体がキャリブレーション精度に影響しうるため，±0.05の感度分析を併せて行う",
], Inches(0.7), Inches(4.9), Inches(11.9), Inches(1.5), size=19, spacing=10)


# ══════════════════════════════════════════════════════════════
# 20. CoTを独立条件にしない理由
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "CoT（Chain-of-Thought）を独立条件にしない理由", 20)
bullet_box(sl, [
    "(1) 推論の一貫性向上が過信助長につながる場合がある",
    "(2) 正答率自体を変化させるため確信度設計の効果と分離困難",
    "(3) 条件数倍増によるコスト増大",
    "→ CoTはXiong 2024で評価済みだが，本研究では採用せず将来の拡張として位置づける",
], Inches(0.7), Inches(1.9), Inches(11.9), Inches(4.3), size=22, spacing=18)


# ══════════════════════════════════════════════════════════════
# 21. 評価指標：ECE
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "評価指標①：ECE（Expected Calibration Error）", 21)
add_table(sl,
          headers=["項目", "内容"],
          rows=[
              ["定義", "確信度と実際の正答率のズレの重み付き平均"],
              ["数式", "ECE = Σ_m (|Bm|/n)・|acc(Bm) − conf(Bm)|"],
              ["変数の意味", "M:ビン数, Bm:m番目のビンの集合, n:サンプル総数, acc/conf(Bm):ビン内平均正答率/確信度"],
              ["値の範囲", "0以上（0〜1に収まる）"],
              ["大小の意味", "0に近いほど良い（確信度と正答率が一致）"],
              ["似た指標との違い", "Brier Scoreはビン分割不要，AUROCは識別能力を測る"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(4.9), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 22. 評価指標：Brier Score
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "評価指標②：Brier Score", 22)
add_table(sl,
          headers=["項目", "内容"],
          rows=[
              ["定義", "予測確信度と正誤ラベルの二乗誤差の平均"],
              ["数式", "BS = (1/N)・Σ_i (p_i − y_i)^2"],
              ["変数の意味", "N:問題数, p_i:i番目の問題への予測確信度, y_i:正誤（正解=1，不正解=0）"],
              ["値の範囲", "0以上（0〜1に収まる）"],
              ["大小の意味", "0に近いほど良い"],
              ["似た指標との違い", "Proper Scoring Ruleとして理論的保証あり，ビン分割不要（ECEとの違い）"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(4.9), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 23. 評価指標：AUROC
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "評価指標③：AUROC", 23)
add_table(sl,
          headers=["項目", "内容"],
          rows=[
              ["定義", "正解サンプルの確信度が不正解サンプルの確信度を上回る確率"],
              ["数式", "AUROC = (1/|Pos||Neg|)・ΣΣ [1(p>q) + 0.5・1(p=q)]"],
              ["変数の意味", "Pos:正解サンプルの確信度集合, Neg:不正解サンプルの確信度集合, p,q:各集合から取り出した確信度"],
              ["値の範囲", "0〜1"],
              ["大小の意味", "1に近いほど識別能力が高い。0.5はランダム（無意味な識別）"],
              ["似た指標との違い", "ECE等の「較正」ではなく「識別能力」を測る。両者は独立に評価する必要がある"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(4.9), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 24. 正答判定方法
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "正答判定方法", 24)
bullet_box(sl, [
    "数学（MGSM）：正規化完全一致（抽出数値 == 正解数値）",
    "常識・知識（JCommonsenseQA・JMMLU）：選択肢ラベル一致",
    "翻訳（FLORES-200）：COMETスコア閾値（50文の人間二値判定でF1最適化して決定）",
    "翻訳のLLM-as-a-Judgeは主判定ではなく境界サンプルの検証手段としてのみ使用",
    "翻訳ドメインでは閾値±0.05の感度分析をECEと併せて報告",
], Inches(0.7), Inches(1.8), Inches(11.9), Inches(4.5), size=20, spacing=14)


# ══════════════════════════════════════════════════════════════
# 25. 実験統制
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "実験統制", 25)
bullet_box(sl, [
    "temperature=0で全モデルへ問い合わせ，同一問題への確信度ばらつきを排除",
    "システムプロンプトは使用せず，モデルデフォルト動作への影響を排除",
    "確信度を解析できないケースは分母から除外して集計。失敗率もモデル・方式ごとに報告",
    "APIのレート制限に対してexponential backoffによる自動再試行を実装（run_pilot.pyに実装済み）",
], Inches(0.7), Inches(1.8), Inches(11.9), Inches(4.5), size=20, spacing=16)


# ══════════════════════════════════════════════════════════════
# 26. 検証仮説
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "検証仮説：自分はこう予想している", 26)
add_table(sl,
          headers=["仮説", "内容", "根拠・予想の理由"],
          rows=[
              ["H1", "Verb.2SはVerb.1SよりECEを改善", "2段階の自己参照が確信度スケールを較正。回答後の確信度質問で接地が生じる（ADVICE診断的知見）"],
              ["H2", "Ling.1Sは数値表現方式より改善幅が小さい", "離散的な言語→数値マッピングが情報を圧縮するため"],
              ["H3", "改善幅はタスクドメインにより異なる", "ドメインごとの正答率分布・難易度の違い"],
              ["H4", "日本語での改善幅は英語より小さい", "MlingConfの実測でも日本語ECEが英語より悪化する傾向（例：16.52→34.49）"],
          ],
          x=Inches(0.5), y=Inches(1.5), w=Inches(12.35), h=Inches(4.9), header_size=17, body_size=15)


# ══════════════════════════════════════════════════════════════
# 27. 想定される結果パターン
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "想定される結果パターンと考察方針", 27)
bullet_box(sl, [
    "(a) 方式間で明確な差 → 統計検定（Friedman/Wilcoxon）で有意性を確認し，設計上の違いを考察",
    "(b) 方式間に有意差なし → 「差がない」こと自体を報告し，先行研究（MlingConf等）と対比",
    "(c) モデルにより効果が異なる → 指示追従能力・学習データの違いとの関連を考察",
    "モデル×方式の結果空間に対して排他的・網羅的に分類できることを確認済み",
    "いずれの結果になっても報告可能な知見として整理する方針",
], Inches(0.7), Inches(1.8), Inches(11.9), Inches(4.6), size=19, spacing=14)


# ══════════════════════════════════════════════════════════════
# 28. 進捗：データセット・プロンプト・評価指標
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "現在の進捗①：データセット・プロンプト・評価指標", 28)
bullet_box(sl, [
    "4ドメインのデータセット・正答判定基準を先行研究と比較したうえで確定",
    "3方式×4ドメインのプロンプトテンプレートを実装（Verb.2Sの2ターン処理を含む）",
    "確信度の自動解析処理，言語表現→数値の対応表を実装",
    "ECE・Brier Score・AUROCを計算するプログラムを実装し，人工データで理論値と一致することを数値的に確認",
], Inches(0.7), Inches(1.8), Inches(11.9), Inches(4.5), size=20, spacing=16)


# ══════════════════════════════════════════════════════════════
# 29. 進捗：実験実行スクリプト・先行研究の再調査
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "現在の進捗②：実験実行スクリプト・先行研究の再調査", 29)
bullet_box(sl, [
    "3方式対応の実験実行スクリプト（run_pilot.py）を整備",
    "OpenAI/Anthropic/Gemini各APIへの呼び出し，確信度の正規化，レート制限対策を実装",
    "MlingConfが日本語含む多言語で確信度手法の検証を既に行っていることを確認し，新規性の主張を精緻化",
    "Jang et al. 2025の誤引用（Verb.2Sの根拠として不適切）を発見・訂正",
    "一方，実際のAPIを用いた実験は未実施であり，実測データはまだ得られていない",
], Inches(0.7), Inches(1.7), Inches(11.9), Inches(4.7), size=19, spacing=13)


# ══════════════════════════════════════════════════════════════
# 30. 今後：直近のスケジュール
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "今後の予定：直近のスケジュール", 30)
bullet_box(sl, [
    "2026年7月中旬：パイロット実験でスクリプトの動作確認",
    "2026年7月17日：中間発表概要2ページをLETUSに提出（12:00締切）",
    "2026年7月20〜27日：中間発表会（6分＋質疑3分）／8月5日：再発表日（必要な場合）",
    "2026年8〜9月：本実験実施（4〜6モデル×3方式×1,000問）",
    "2026年10〜11月：結果分析・統計検定・各章の草稿完成",
    "2026年12月：最終稿作成／2027年1月：卒業論文提出",
], Inches(0.7), Inches(1.7), Inches(11.9), Inches(4.8), size=19, spacing=13)


# ══════════════════════════════════════════════════════════════
# 31. Murphy分解の扱い
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "Murphy分解（探索的オプション）の扱い", 31)
bullet_box(sl, [
    "研究の方針の主軸はECE・Brier Score・AUROCの3指標。Murphy分解の採用は確定していない",
    "本実験データが十分に得られた場合にのみ，補足的な考察として検討する",
    "BS = REL − RES + UNC。RELは較正誤差（低いほど良い），RESは識別能力（高いほど良い）",
], Inches(0.7), Inches(1.7), Inches(11.9), Inches(2.2), size=19, spacing=12)
add_table(sl,
          headers=["採否の判断基準", "判断"],
          rows=[
              ["条件間でRELとRESが逆方向に動くケースがある", "採用：機序の説明に使える"],
              ["RELの順位がECEの順位と完全に一致", "破棄：ECEと重複"],
              ["RESの順位がAUROCの順位と完全に一致", "破棄：AUROCと重複"],
          ],
          x=Inches(0.7), y=Inches(4.1), w=Inches(11.9), h=Inches(2.3), header_size=16, body_size=15)


# ══════════════════════════════════════════════════════════════
# 32. スコープ縮小トリガー・予想される成果
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "スコープ縮小のトリガー・予想される成果", 32)
add_text(sl, "スコープ縮小のトリガー（進捗が遅れた場合）", Inches(0.7), Inches(1.5), Inches(11.9), Inches(0.4),
          size=19, bold=True, color=C_ACCENT)
bullet_box(sl, [
    "レベル1（7月末50%未達）：3モデル×3プロンプト方式に縮小",
    "レベル2（9月末40%未達）：2モデル×2ドメイン×2プロンプト方式",
    "レベル3（11月末30%未達）：Claude単独×2ドメイン×50問（論文成立最低ライン）",
], Inches(0.9), Inches(1.95), Inches(11.5), Inches(1.6), size=17, spacing=8)
add_text(sl, "予想される成果", Inches(0.7), Inches(3.7), Inches(11.9), Inches(0.4),
          size=19, bold=True, color=C_ACCENT)
bullet_box(sl, [
    "日本語タスクにおける複数モデルのキャリブレーション性能の定量的評価",
    "プロンプト方式による性能差の特定と最適方式の提案",
    "ドメイン依存性の可視化，日本語vs英語での性能差に関する知見",
], Inches(0.9), Inches(4.15), Inches(11.5), Inches(1.6), size=17, spacing=8)


# ══════════════════════════════════════════════════════════════
# 33. 必要なリソース・リスク
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "必要なリソースとコスト・リスクと対応策", 33)
add_text(sl, "API使用料：約1,500〜3,000円（研究室予算50,000円の約6%以内）",
          Inches(0.7), Inches(1.5), Inches(11.9), Inches(0.5), size=18, color=C_DARK)
add_table(sl,
          headers=["リスク", "影響", "対応策"],
          rows=[
              ["API費用の超過", "中", "問題数を減らす，無料枠活用"],
              ["モデルバージョン変更", "中", "使用日時を記録，再現不能を明示"],
              ["データセットの正解精度", "高", "複数ソース，人手での再確認"],
              ["思ったほど差が出ない", "中", "「差がない」ことも成果として報告"],
              ["時間超過", "中", "実験3（日英比較）を省略可能と位置づけ"],
          ],
          x=Inches(0.7), y=Inches(2.15), w=Inches(11.9), h=Inches(4.1), header_size=16, body_size=15)


# ══════════════════════════════════════════════════════════════
# 34. 参考文献
# ══════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "参考文献", 34)
refs = [
    "Ji et al. (2023) — Survey of Hallucination in NLG",
    "Guo et al. (2017, ICML) — On Calibration of Modern Neural Networks",
    "Kadavath et al. (2022) / Lin et al. (2022) — LLMの自己評価・言語化",
    "Tian et al. (2023, EMNLP) / Xiong et al. (2024, ICLR) — Verbalized Confidence",
    "Xue et al. (2025, ACL Findings) — MlingConf",
    "Xie et al. (2024) — Black-Box Calibration Survey / Adaptive Temperature Scaling",
    "Murphy (1973) / Bröcker (2009) / Pohle (2020) / Ferro & Fricker (2012) — Murphy分解",
    "Rei et al. (2020) / Zhang et al. (2020) / Kocmi & Federmann (2023) — 翻訳評価",
    "その他：詳細は abstract_full_v1.tex 参考文献（全33本）を参照",
]
add_text(sl, "\n".join(refs), Inches(0.7), Inches(1.7), Inches(11.9), Inches(5.0),
          size=17, color=C_DARK)


prs.save("research/presentations/abstract-full-explainer-slides.pptx")
print("Saved: research/presentations/abstract-full-explainer-slides.pptx")
print(f"Total slides: {len(prs.slides._sldIdLst)}")
