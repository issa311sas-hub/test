# 卒論ビルド用 Makefile
# 使い方: make (ビルド) / make clean (掃除) / make watch (自動ビルド)

MAIN = main
LATEX = lualatex
BIBER = biber

.PHONY: all clean watch

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex chapters/*.tex references.bib
	$(LATEX) $(MAIN)
	$(BIBER) $(MAIN)
	$(LATEX) $(MAIN)
	$(LATEX) $(MAIN)

clean:
	rm -f $(MAIN).{aux,bbl,bcf,blg,log,out,pdf,run.xml,toc,lof,lot}

watch:
	@echo "Watching for changes... (Ctrl+C to stop)"
	@while true; do \
		inotifywait -q -e modify $(MAIN).tex chapters/*.tex references.bib 2>/dev/null || sleep 2; \
		$(MAKE) all; \
	done
