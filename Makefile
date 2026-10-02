.PHONY: all build serve serve-sciance serve-spec publish-sciance test clean examples build-multiscale build-sciance build-mindmatter build-autoresearch

all: build

build: build-multiscale

build-multiscale:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --web-dir docs/

build-sciance:
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir docs/

build-mindmatter:
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --web-dir docs/

build-autoresearch:
	python3 -m cli.compiler --spec examples/autoresearch-wild/02-city-spec.json --web-dir docs/

serve:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --web-dir docs/ --serve 8080

# SCIANCE showcase in its own build folder (dist/ is git-ignored, docs/ stays untouched)
SCIANCE_PORT ?= 8088
serve-sciance:
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir dist/sciance/ --serve $(SCIANCE_PORT)

# Preview any spec kept outside this repo (e.g. private project maps): builds into git-ignored dist/
#   make serve-spec SPEC=~/path/02-city-spec.json [NAME=my-map] [PORT=8090]
NAME ?= local
PORT ?= 8090
serve-spec:
	@test -n "$(SPEC)" || { echo "[!] Usage: make serve-spec SPEC=path/to/02-city-spec.json [NAME=…] [PORT=…]"; exit 1; }
	python3 -m cli.compiler --spec $(SPEC) --web-dir dist/$(NAME)/ --serve $(PORT)

# Publish the SCIANCE showcase to its GitHub Pages repo (omniscale-ai/sciance-d1-1-metropolis).
# Builds and commits in the local checkout; pushing stays a deliberate, manual step.
SCIANCE_PAGES_DIR ?= ../sciance-d1-1-metropolis
publish-sciance:
	@test -d $(SCIANCE_PAGES_DIR)/.git || { echo "[!] $(SCIANCE_PAGES_DIR) is not a git checkout (clone git@github.com:omniscale-ai/sciance-d1-1-metropolis.git there)"; exit 1; }
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --web-dir $(SCIANCE_PAGES_DIR)/
	mkdir -p $(SCIANCE_PAGES_DIR)/spec
	cp examples/sciance-materials/01-domain-profile.yaml examples/sciance-materials/02-city-spec.json $(SCIANCE_PAGES_DIR)/spec/
	@cd $(SCIANCE_PAGES_DIR) && git add -A && if git diff --cached --quiet; then echo "[=] Nothing to publish: the Pages repo is up to date"; else \
		git commit -q -m "Update map from metropolis-kit $$(git -C $(CURDIR) describe --always --dirty)" && \
		echo "[+] Committed in $(SCIANCE_PAGES_DIR). Review, then push: git -C $(SCIANCE_PAGES_DIR) push"; fi

examples:
	@echo "[*] Compiling AI Multiscale showcase..."
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --out examples/ai-multiscale/city-data.js
	@echo "[*] Compiling SCIANCE showcase..."
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --out examples/sciance-materials/city-data.js
	@echo "[*] Compiling MIND-MATTER showcase..."
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --out examples/mind-matter/city-data.js
	@echo "[*] Compiling AUTORESEARCH IN THE WILD showcase..."
	python3 -m cli.compiler --spec examples/autoresearch-wild/02-city-spec.json --out examples/autoresearch-wild/city-data.js

test:
	python3 -m cli.compiler --spec examples/ai-multiscale/02-city-spec.json --validate-only
	python3 -m cli.compiler --spec examples/sciance-materials/02-city-spec.json --validate-only
	python3 -m cli.compiler --spec examples/mind-matter/02-city-spec.json --validate-only
	python3 -m cli.compiler --spec examples/autoresearch-wild/02-city-spec.json --validate-only

clean:
	rm -rf __pycache__ cli/__pycache__
