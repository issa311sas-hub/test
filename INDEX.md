# 卒業研究プロジェクト インデックス

> **最終更新**: 2026年5月25日（ゼミ承認版 v0.3 反映）
> **テーマ**: プロンプト設計による大規模言語モデルのキャリブレーション性能向上に関する研究
> **ステータス**: 🟢 研究方向性承認済み（2026-05-20 ゼミ発表にて指導教員承認）
> **作業ブランチ**: `claude/thesis-planning-multi-agent-oBNwO`

---

## 🚨 運用方針（最終更新: 2026-05-25）

1. **本人の作業時間**: 週 2 時間から**増加（時間制約を緩和）**（`research/scope-revision-plan.md`）
2. **指導教員**: 多忙でメール返信が期待できない → **教員返信を待たずに autonomous 進行**
3. **研究室予算**: 年 50,000 円まで使用可（`research/budget-tracker.md`）
4. **ゴール優先順位**: 「通すこと」 > 面白さ > 学会発表
5. **提出期限**: **1 月中**（具体日は未定、2026-04-10 本人確認）
6. **中間発表（卒業研究1）**: 
   - 概要提出: **2026-07-17（金）12:00 厳守** / LETUS
   - 発表会: **2026-07-20（月）〜 07-27（月）** の期間 / グループ別
   - 再発表日: **2026-08-05（水）**
   - 形式: スライド 6 分発表 + 質疑 3 分、概要 2 ページ PDF
7. **執筆ツール**: **LaTeX**
8. **Python 環境**: pip / Anaconda 利用可能（構築済み）
9. **API キー**: 本人立替精算

### Claude の役割分担（2026-05-25 更新）

| 成果物 | Claude の担当 | ユーザーの担当 |
|---|---|---|
| 論文本文 | 章草稿の生成・推敲補助 | 構成判断・考察・最終執筆 |
| **スライド** | **たたき台（構成・内容案）まで** | **デザイン・仕上げ・発表** |
| 実験スクリプト | 実装・保守 | 実行・結果解釈 |
| 文献要約 | 要約・精読ガイド生成 | 精読・理解の確認 |
| データセット | 問題雛形生成・チェック補助 | 最終確認・品質判断 |

---

## 🎯 現在のフェーズ

**第1フェーズ: 準備期（4月〜5月）**
- ✅ テーマの方向性決定（仮）
- ✅ 自己分析（Q1, Q3-Q10 完了、Q2 は本人記入待ち）
- ✅ DEL フレーミング案の作成
- ✅ スコープ改訂プランの策定
- ⏳ 指導教員への初回相談メール（返信不問で送信）
- ⏳ 先行研究の精読
- ⏳ データセット構築
- ⏳ パイロット実験の実施

---

## 📁 ファイル構成

### 📘 ルート
- [thesis-plan.md](thesis-plan.md) — **全体の計画書**（フェーズ別・月別タスク）
- [INDEX.md](INDEX.md) — このファイル（ナビゲーション）

### 📝 templates/（汎用テンプレート）
- [literature-card.md](templates/literature-card.md) — 文献要約カードテンプレート
- [research-note.md](templates/research-note.md) — 研究ノートの日次テンプレート
- [submission-checklist.md](templates/submission-checklist.md) — 卒論提出要項チェックリスト
- [weekly-checkin.md](templates/weekly-checkin.md) — 週次チェックインテンプレート
- [monthly-review.md](templates/monthly-review.md) — 月次レビューテンプレート
- [experiment-log.md](templates/experiment-log.md) — 実験ログテンプレート
- [self-analysis-worksheet.md](templates/self-analysis-worksheet.md) — 自己分析 10 問ワークシート（仮テーマ適合度検証用）

### 📅 daily-log/（日次ログ）
- [2026-04-09.md](daily-log/2026-04-09.md) — 4/9 の作業記録（autonomous session の実績）
- [2026-04-10.md](daily-log/2026-04-10.md) — 4/10 の予定（週 2h 予算内で 4 タスク）
- [2026-04-11.md](daily-log/2026-04-11.md) — 4/11 の予定（Kadavath 2022 精読集中日）
- [self-analysis-2026-04-09.md](daily-log/self-analysis-2026-04-09.md) — **自己分析（本人情報反映済み、Q2 のみ未記入）**

### 🔬 research/（研究関連ドキュメント）

#### テーマ決定プロセス
- [ai-theme-candidates.md](research/ai-theme-candidates.md) — 20候補の洗い出し（8カテゴリ）
- [theme-evaluation.md](research/theme-evaluation.md) — ルーブリック評価（上位3候補選定）
- [theme-deep-dive.md](research/theme-deep-dive.md) — トップ3の詳細分析と仮決定
- [theme-selection-process-guide.md](research/theme-selection-process-guide.md) — テーマ決定プロセスの設計書（参考資料）
- [ai-research-landscape-reference.md](research/ai-research-landscape-reference.md) — 学部卒論向け AI 研究テーマ広域サーベイ（参考資料・辞書用途）

#### 研究計画・運営
- [research-proposal-draft.md](research/research-proposal-draft.md) — 研究計画書草稿 v0.1
- [literature-list.md](research/literature-list.md) — 先行研究リスト（シード 15 本＋DEL 7 件、精読目標 8 本）
- [references.bib](research/references.bib) — BibTeX データベース（約 25 エントリ、DEL 含む）
- [pilot-experiment-design.md](research/pilot-experiment-design.md) — パイロット実験設計書
- [dataset-construction-guide.md](research/dataset-construction-guide.md) — データセット構築ガイド（原計画 200 問、改訂 100 問）
- [advisor-email-draft.md](research/advisor-email-draft.md) — 指導教員への相談メール（autonomous 版推奨）
- [advisor-meeting-prep.md](research/advisor-meeting-prep.md) — 初回面談の準備パック（DEL フレーミング反映済み）
- [advisor-theme-alignment.md](research/advisor-theme-alignment.md) — **仮テーマと指導教員専門（DEL）の整合性分析**
- [scope-revision-plan.md](research/scope-revision-plan.md) — **週 2h 予算前提のスコープ改訂プラン（4 レベル縮小案）**
- [midterm-presentation-plan.md](research/midterm-presentation-plan.md) — **中間発表（7/17 概要提出・7/20-27 発表）の準備プラン**
- [del-cheatsheet.md](research/del-cheatsheet.md) — DEL の最小限チートシート（面談用）
- [risk-register.md](research/risk-register.md) — リスク台帳（23 リスク、R-022/R-023 中間発表関連を追加）
- [budget-tracker.md](research/budget-tracker.md) — 研究予算トラッカー（年 50,000 円 研究室負担確定）

#### 文献カード（lit-cards/）
- [guo_2017_calibration.md](research/lit-cards/guo_2017_calibration.md) — ECE 原典（記入例）
- [kadavath_2022_language_models_know.md](research/lit-cards/kadavath_2022_language_models_know.md) — 最重要先行研究（記入例）
- [tian_2023_just_ask.md](research/lit-cards/tian_2023_just_ask.md) — verbalized confidence 方法論の根拠（記入例）

#### 論文ドラフト
- [thesis-outline.md](research/thesis-outline.md) — 卒論全体のアウトライン
- [thesis-drafts/chapter1-introduction-draft.md](research/thesis-drafts/chapter1-introduction-draft.md) — 第1章 序論 v0.1
- [thesis-drafts/chapter2-related-work-draft.md](research/thesis-drafts/chapter2-related-work-draft.md) — 第2章 関連研究 v0.1
- [thesis-drafts/chapter3-methods-draft.md](research/thesis-drafts/chapter3-methods-draft.md) — 第3章 研究方法 v0.1
- [thesis-drafts/chapter4-results-skeleton.md](research/thesis-drafts/chapter4-results-skeleton.md) — 第4章 実験結果 骨組み
- [thesis-drafts/chapter5-discussion-skeleton.md](research/thesis-drafts/chapter5-discussion-skeleton.md) — 第5章 考察 骨組み
- [thesis-drafts/chapter6-conclusion-skeleton.md](research/thesis-drafts/chapter6-conclusion-skeleton.md) — 第6章 結論 骨組み

### 📄 latex/（LaTeX 卒論テンプレート）
- [main.tex](latex/main.tex) — メインファイル（LuaLaTeX + biblatex）
- [chapters/](latex/chapters/) — 各章の .tex ファイル（chapter1〜6）
- [references.bib](latex/references.bib) — 参考文献 DB（research/ のコピー）
- [Makefile](latex/Makefile) — ビルド自動化（`make` で PDF 生成）
- [README.md](latex/README.md) — LaTeX 環境の説明

### 💻 research/experiment/pilot/（パイロット実験コード）
- [README.md](research/experiment/pilot/README.md) — 使い方ドキュメント
- [requirements.txt](research/experiment/pilot/requirements.txt) — Python依存
- [prompts.py](research/experiment/pilot/prompts.py) — プロンプトテンプレート
- [parser.py](research/experiment/pilot/parser.py) — 応答パーサー
- [calibration.py](research/experiment/pilot/calibration.py) — ECE/Brier/AUROC計算
- [run_pilot.py](research/experiment/pilot/run_pilot.py) — メイン実行（OpenAI/Anthropic）
- [mock_run.py](research/experiment/pilot/mock_run.py) — API不要のモック実行
- [visualize.py](research/experiment/pilot/visualize.py) — Reliability Diagram 生成
- [questions_sample.csv](research/experiment/pilot/questions_sample.csv) — サンプル50問
- [test_parser.py](research/experiment/pilot/test_parser.py) — パーサーの単体テスト（21件）
- [test_calibration.py](research/experiment/pilot/test_calibration.py) — 指標計算のテスト（14件）
- [generate_dummy_figures.py](research/experiment/pilot/generate_dummy_figures.py) — 論文 Figure 5-1〜5-4 のダミー生成
- [summarize_results.py](research/experiment/pilot/summarize_results.py) — 実験結果 CSV から Markdown サマリを自動生成
- [PRE_FLIGHT_CHECKLIST.md](research/experiment/pilot/PRE_FLIGHT_CHECKLIST.md) — 本番 API 実行前の離陸前チェック（予算ミス防止）

---

## ✅ 完了済みタスク（2026-04-09）

### テーマ決定プロセス
- [x] AI卒論テーマの8カテゴリ分類
- [x] 20個の具体的候補の洗い出し
- [x] 6軸ルーブリックによる評価
- [x] トップ3候補の詳細分析
- [x] 仮テーマの決定

### 研究計画
- [x] 研究計画書草稿（v0.1）の作成
- [x] 先行研究リスト（15本）の整備
- [x] パイロット実験の詳細設計
- [x] 指導教員への相談メール3パターン
- [x] データセット構築ガイドの作成
- [x] 卒論の詳細アウトライン

### コード実装
- [x] プロンプトテンプレート（4種類）
- [x] 応答パーサー（3モード対応）
- [x] Calibration 指標計算（ECE/Brier/AUROC/Reliability Diagram）
- [x] パイロット実行スクリプト（OpenAI/Anthropic）
- [x] モック実行スクリプト（API不要）
- [x] 可視化スクリプト（matplotlib）
- [x] 単体テスト 35件（全てパス）
- [x] 統合テスト（50問のモック実行で end-to-end 動作確認）

### 論文執筆
- [x] 卒論の詳細アウトライン（6章構成に再編）
- [x] 第1章 序論 v0.1
- [x] 第2章 関連研究 v0.1
- [x] 第3章 研究方法 v0.1
- [x] 第4章 実験結果 骨組み
- [x] 第5章 考察 骨組み
- [x] 第6章 結論 骨組み
- [x] BibTeX 参考文献 DB（約20エントリ）
- [x] 論文 Figure 5-1〜5-4 のダミー版生成

### プロジェクト運営
- [x] リスク台帳（17 リスク、影響度×可能性で整理）
- [x] 週次チェックインテンプレート
- [x] 月次レビューテンプレート
- [x] 指導教員初回面談の準備パック

---

## ⏳ 次のアクション（優先順位順・週 2h 予算）

### 4/10 金（メール送信依頼済み）
1. ~~指導教員への初回相談メール送信~~（**送信依頼済み・本人対応待ち**）
2. Zotero の最小インストール（40 分）
3. 自己分析 Q2 の記入（20 分）
4. DEL 入門資料の取り寄せ手配（10 分）

### 4/11 土（本日）〜4/12 日（週末集中）
5. **Kadavath 2022 の精読**（最優先、2〜3 時間）
6. Zotero の詳細設定（余裕があれば）
7. LaTeX テンプレートの確認（AI が雛形を用意済み）

### 今月中（4月）
7. Guo 2017 / Tian 2023 の精読（各 2 時間）
8. 提出要項を学科事務で確認（月曜以降）
9. van Ditmarsch の DEL 教科書の 1-2 章を斜め読み
10. 指導教員との面談（廊下立ち話・ゼミ後の 5 分でも OK）

### 5月
11. 先行研究 8 本精読完了（原計画 15 本から縮減）
12. データセット設計完了（100 問、原計画 200 問から縮減）
13. 研究計画書 v1.0（DEL フレーミング版）の作成

---

## 🚨 要確認事項（指導教員に聞くべきこと）

> **2026-04-13 更新**: 指導教員より初回メール返信を受領。
> 「今の段階で指示することはない、勝手にやっていい」の趣旨で、
> autonomous 進行および DEL フレーミングが実質承認された。
> 以下、関連事項を更新。

- [x] ~~**DEL フレーミング（LLM を認識エージェントとして扱う）を承認するか？**~~ → **実質 greenlit**（2026-04-13 返信、異議なし）
- [ ] S5 系と KD45 系のどちらを理論的ベースラインとすべきか？（ゼミ初回で軽く伺う）
- [x] ~~テーマの方向性は研究室の専門と整合するか？~~ → **問題なし**（返信で異議なし）
- [ ] 倫理審査は本当に不要か？（学科事務に別途確認）
- [x] ~~API費用は研究室で負担可能か？~~ → **年 50,000 円まで OK（本人確認済み）**
- [x] ~~研究室名義の API キー発行と本人立替精算のどちらが楽か？~~ → **本人立替精算**（2026-04-10 確認）
- [ ] 提出要項の特殊事項（フォーマット・字数）— LaTeX 確定済み、細かい書式要件は事務確認
- [x] ~~中間報告のタイミング~~ → **7/20〜7/27 発表、7/17 概要提出、再発表 8/5**（2026-04-13 本人共有）
- [ ] 所属グループ・発表日時・発表場所（後日掲示 → 要継続確認）
- [ ] LETUS 提出方法の詳細（PDF 形式の要件）
- [ ] 学会発表の可能性（IPSJ / 言語処理学会など）— ゼミ始動後に伺う
- [x] ~~週 2 時間という本人の作業時間制約は許容範囲か？~~ → **問題なし**（「勝手にやっていい」で裁量付与）

---

## 📊 進捗サマリー

| カテゴリ | 進捗 |
|---|---|
| テーマ決定 | 🟢 仮決定済み + DEL フレーミング（2026-04-13 教員返信で実質承認） |
| 自己分析 | 🟡 Q1, Q3-Q10 記入済み / Q2 のみ残 |
| 先行研究調査 | 🔴 0/8 本精読済み（目標を 15→8 本に縮減） |
| 研究計画書 | 🟡 v0.1 作成済み / v1.0（DEL 版）はゼミ初回持参用に本人推敲中 |
| スコープ計画 | 🟢 4 レベル縮小案と月次マイルストーン整備 |
| データセット | 🟡 サンプル50問のみ（目標を 200→100 問に縮減） |
| 実験コード | 🟢 雛形完成・テスト 35 件パス・PRE_FLIGHT_CHECKLIST 整備 |
| 論文執筆 | 🟡 3章分の草稿＋3章分の骨組み |
| リスク管理 | 🟢 23 リスク（R-022/R-023 中間発表関連を追加） |
| 予算管理 | 🟢 研究室負担 50,000 円 確定・トラッカー整備 |
| テンプレート | 🟢 7 種完備（自己分析ワークシート含む） |
| 文献カード | 🟡 3件の記入例 |

凡例: 🟢 順調 / 🟡 着手済み / 🔴 未着手

---

## 💡 重要な決定事項

1. **仮テーマ**: LLMの自己評価能力検証（verbalized confidence calibration）
   - 理由: 個人完結・ホット・実装簡単・結果が明確
   - **DEL フレーミング**: 動的認識論理の実証実験として位置づけ（**2026-04-13 教員返信で実質承認**）
2. **実験対象**: GPT, Claude, Gemini, 日本語特化モデル計4モデル
3. **ドメイン**: 常識・数学・歴史・翻訳の4種
4. **問題数**: 本実験 **100 問**（原計画 200 問から縮減）、パイロット 50 問
5. **主要指標**: ECE, Brier Score, AUROC
6. **開発言語**: Python（pandas, matplotlib, 各モデルAPI）
7. **再現性**: 全コードをGitで公開
8. **スコープ**: レベル 0 で計画、進捗次第でレベル 1〜3 に縮小（`scope-revision-plan.md`）
9. **作業分担**: AI が下書き・実装・集計、本人は意思決定・検証・考察のみ
10. **予算**: 年 50,000 円（研究室負担確定）
11. **執筆ツール**: LaTeX（本人確認 2026-04-10）
12. **提出期限**: 1 月中（具体日未定）
13. **中間発表**: 7 月頃

---

## ⚠️ 注意事項

- **APIキーは絶対にコミットしない**（`.gitignore` で対策済み）
- **モデルのバージョン・実行日時は必ず記録**（再現性のため）
- **指導教員との相談なしで大幅な方向転換はしない**
- **パイロットの結果が出るまで本実験に進まない**

---

## 📞 連絡・相談先

- **指導教員**: （連絡先を記入）
- **学科事務**: （連絡先を記入）
- **先輩（メンター）**: （連絡先を記入）

---

## 🔖 明日から動くためのクイックリファレンス

### 文献を1本読んだ時
```bash
cp templates/literature-card.md research/lit-cards/著者_年_タイトル.md
# カードを埋めて research/literature-list.md に反映
```

### 研究ノート（日次）を書く時
```bash
cp templates/research-note.md daily-log/2026-MM-DD.md
```

### パイロット実験を回す時
```bash
cd research/experiment/pilot
cp .env.example .env   # 初回のみ、APIキーを埋める
make test              # テストが通るか確認
make mock              # モック実行で挙動確認
# 本番:
make pilot-openai      # OpenAI で実行
make summary           # 結果を Markdown 集計
```

### 指導教員面談の前
1. `research/advisor-meeting-prep.md` を開く
2. 想定質問への回答を見直す
3. 議事録テンプレートを `daily-log/2026-MM-DD.md` にコピー

### 週次レビュー（日曜）
```bash
mkdir -p daily-log/weekly
cp templates/weekly-checkin.md daily-log/weekly/2026-WXX.md
```

### 月次レビュー（月末）
```bash
mkdir -p daily-log/monthly
cp templates/monthly-review.md daily-log/monthly/2026-MM.md
```

### リスク・予算の見直し（月1回）
- `research/risk-register.md` を開いて各リスクのステータスを更新
- `research/budget-tracker.md` に今月の支出を記入
