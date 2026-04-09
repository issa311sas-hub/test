# 卒業研究プロジェクト インデックス

> **最終更新**: 2026年4月9日
> **仮テーマ**: LLMの自己評価能力の検証 —— 日本語 Verbalized Confidence Calibration の実証分析
> **作業ブランチ**: `claude/thesis-planning-multi-agent-oBNwO`

---

## 🎯 現在のフェーズ

**第1フェーズ: 準備期（4月〜5月）**
- ✅ テーマの方向性決定（仮）
- ⏳ 指導教員への初回相談（次のアクション）
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

### 📅 daily-log/（日次ログ）
- [2026-04-09.md](daily-log/2026-04-09.md) — 本日の作業記録

### 🔬 research/（研究関連ドキュメント）

#### テーマ決定プロセス
- [ai-theme-candidates.md](research/ai-theme-candidates.md) — 20候補の洗い出し（8カテゴリ）
- [theme-evaluation.md](research/theme-evaluation.md) — ルーブリック評価（上位3候補選定）
- [theme-deep-dive.md](research/theme-deep-dive.md) — トップ3の詳細分析と仮決定

#### 研究計画・運営
- [research-proposal-draft.md](research/research-proposal-draft.md) — 研究計画書草稿 v0.1
- [literature-list.md](research/literature-list.md) — 先行研究リスト（シード15本）
- [references.bib](research/references.bib) — BibTeX データベース（約20エントリ）
- [pilot-experiment-design.md](research/pilot-experiment-design.md) — パイロット実験設計書
- [dataset-construction-guide.md](research/dataset-construction-guide.md) — 200問データセット構築ガイド
- [advisor-email-draft.md](research/advisor-email-draft.md) — 指導教員への相談メール3パターン
- [advisor-meeting-prep.md](research/advisor-meeting-prep.md) — 初回面談の準備パック
- [risk-register.md](research/risk-register.md) — リスク台帳（17 リスク）

#### 論文ドラフト
- [thesis-outline.md](research/thesis-outline.md) — 卒論全体のアウトライン
- [thesis-drafts/chapter1-introduction-draft.md](research/thesis-drafts/chapter1-introduction-draft.md) — 第1章 序論 v0.1
- [thesis-drafts/chapter2-related-work-draft.md](research/thesis-drafts/chapter2-related-work-draft.md) — 第2章 関連研究 v0.1
- [thesis-drafts/chapter3-methods-draft.md](research/thesis-drafts/chapter3-methods-draft.md) — 第3章 研究方法 v0.1
- [thesis-drafts/chapter4-results-skeleton.md](research/thesis-drafts/chapter4-results-skeleton.md) — 第4章 実験結果 骨組み
- [thesis-drafts/chapter5-discussion-skeleton.md](research/thesis-drafts/chapter5-discussion-skeleton.md) — 第5章 考察 骨組み
- [thesis-drafts/chapter6-conclusion-skeleton.md](research/thesis-drafts/chapter6-conclusion-skeleton.md) — 第6章 結論 骨組み

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
- [x] 卒論の詳細アウトライン（7章構成）
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

## ⏳ 次のアクション（優先順位順）

### すぐに（今週中）
1. **指導教員への初回相談メール送信**
   - `research/advisor-email-draft.md` のパターンAを使う
   - 日時を3案提示
2. **Zoteroのインストールと初期設定**
3. **先行研究の精読開始**（Kadavath 2022 / Guo 2017 / Tian 2023）

### 今月中（4月）
4. 先行研究 Week1〜2 の論文を読む
5. 提出要項を学科事務で確認
6. 指導教員との面談

### 5月
7. データセット 200 問の構築
8. パイロット実験の実施（50問 × 2モデル）
9. 研究計画書 v1.0（指導教員承認版）の完成

---

## 🚨 要確認事項（指導教員に聞くべきこと）

- [ ] テーマの方向性は研究室の専門と整合するか？
- [ ] 倫理審査は本当に不要か？
- [ ] API費用は研究室で負担可能か？
- [ ] 提出要項の特殊事項（フォーマット・字数）
- [ ] 中間報告のタイミング
- [ ] 学会発表の可能性

---

## 📊 進捗サマリー

| カテゴリ | 進捗 |
|---|---|
| テーマ決定 | 🟡 仮決定済み（教員承認待ち） |
| 先行研究調査 | 🔴 0/15 本精読済み |
| 研究計画書 | 🟡 v0.1 作成済み |
| データセット | 🟡 サンプル50問のみ |
| 実験コード | 🟢 雛形完成・テスト済み |
| 論文執筆 | 🟡 3章分の草稿＋3章分の骨組み |
| リスク管理 | 🟢 台帳作成済み |
| テンプレート | 🟢 5種完備 |

凡例: 🟢 順調 / 🟡 着手済み / 🔴 未着手

---

## 💡 重要な決定事項

1. **仮テーマ**: LLMの自己評価能力検証（verbalized confidence calibration）
   - 理由: 個人完結・ホット・実装簡単・結果が明確
2. **実験対象**: GPT, Claude, Gemini, 日本語特化モデル計4モデル
3. **ドメイン**: 常識・数学・歴史・翻訳の4種
4. **問題数**: 本実験200問、パイロット50問
5. **主要指標**: ECE, Brier Score, AUROC
6. **開発言語**: Python（pandas, matplotlib, 各モデルAPI）
7. **再現性**: 全コードをGitで公開

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
