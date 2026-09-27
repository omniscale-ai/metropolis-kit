.PHONY: all build serve test clean examples build-multiscale build-sciance build-mindmatter

all: build

build: build-multiscale

build-multiscale:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --web-dir docs/

build-sciance:
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir docs/

build-mindmatter:
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --web-dir docs/

serve:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --web-dir docs/ --serve 8080

examples:
	@echo "[*] Compiling AI Multiscale showcase..."
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --out examples/ai-multiscale/city-data.js
	@echo "[*] Compiling SCIANCE showcase..."
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --out examples/sciance-materials/city-data.js
	@echo "[*] Compiling MIND-MATTER showcase..."
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --out examples/mind-matter/city-data.js

test:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --validate-only
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --validate-only
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --validate-only

clean:
	rm -rf __pycache__ cli/__pycache__
