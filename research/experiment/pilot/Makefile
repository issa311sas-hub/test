# パイロット実験用 Makefile
#
# 使い方例:
#   make test          # 単体テストを実行
#   make mock          # API 不要のモック実行
#   make summary       # 実験結果から Markdown サマリを生成
#   make figures       # ダミー図（論文用）を生成
#   make clean         # results/ を削除
#
# 初回セットアップ:
#   make install       # pip で依存をインストール
#   cp .env.example .env && vim .env  # APIキー設定

PYTHON := python3
PIP := pip3

.PHONY: help install test mock pilot-openai pilot-anthropic summary figures visualize clean

help:
	@echo "使い方: make <target>"
	@echo ""
	@echo "セットアップ:"
	@echo "  install         pip で依存をインストール"
	@echo ""
	@echo "テスト:"
	@echo "  test            parser と calibration の単体テストを実行"
	@echo ""
	@echo "実験:"
	@echo "  mock            API 不要のモック実行（50問）"
	@echo "  pilot-openai    OpenAI API で実行（.env 必要）"
	@echo "  pilot-anthropic Anthropic API で実行（.env 必要）"
	@echo ""
	@echo "分析・可視化:"
	@echo "  summary         results/*.csv から Markdown サマリを生成"
	@echo "  figures         論文用ダミー図（Figure 5-1〜5-4）を生成"
	@echo "  visualize       実行結果の Reliability Diagram を描画"
	@echo ""
	@echo "掃除:"
	@echo "  clean           results/ 内の全ファイルを削除"

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) test_parser.py
	$(PYTHON) test_calibration.py

mock:
	$(PYTHON) mock_run.py --questions questions_sample.csv --output results/mock_run.csv

pilot-openai:
	$(PYTHON) run_pilot.py --model openai --questions questions_sample.csv --output results/pilot_openai.csv

pilot-anthropic:
	$(PYTHON) run_pilot.py --model anthropic --questions questions_sample.csv --output results/pilot_anthropic.csv

summary:
	$(PYTHON) summarize_results.py --input "results/*.csv" --glob --output results/summary.md

figures:
	$(PYTHON) generate_dummy_figures.py

visualize:
	$(PYTHON) visualize.py --input results/mock_run.csv --output results/reliability_diagram.png

clean:
	rm -rf results/*.csv results/*.png results/*.md results/dummy_figures/
	@echo "results/ をクリーンアップしました（ディレクトリ自体は残します）"
