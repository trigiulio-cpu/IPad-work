MAIN = goldie-and-draghino

# Try lualatex first, fall back to pdflatex
ENGINE := $(shell command -v lualatex 2>/dev/null || echo pdflatex)

.PHONY: all clean

all: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex tikz-dragons.sty tikz-scenes.sty
	$(ENGINE) -interaction=nonstopmode $(MAIN).tex
	$(ENGINE) -interaction=nonstopmode $(MAIN).tex

clean:
	rm -f $(MAIN).aux $(MAIN).log $(MAIN).out $(MAIN).pdf
