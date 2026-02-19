.PHONY: help demo fre baseline venv test

help:
	@echo "AURA (Feb 2026) — handy commands"
	@echo
	@echo "make demo        # quick sanity demo (risk card + artifact folder)"
	@echo "make fre INPUT=...  # run FRE-v2 stub on a file"
	@echo "make baseline    # run displacement baseline (needs manifest + optional deps)"
	@echo
	@echo "See Code/README.md for full instructions."

demo:
	PYTHONPATH=src python scripts/demo.py --out runs/demo

fre:
	PYTHONPATH=src python -m aura.fre.run_fre_stub --input "$(INPUT)"

baseline:
	PYTHONPATH=src python -m aura.forensics.run_displacement_baseline \
		--manifest src/aura/data/paired_dataset/manifest.jsonl \
		--out runs/001 \
		--device cpu

venv:
	python -m venv .venv
	. .venv/bin/activate && pip install -e .

test:
	. .venv/bin/activate && python -m unittest discover -s tests -p "test_*.py" -q
