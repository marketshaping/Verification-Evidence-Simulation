# make setup    create .venv and install packages
# make check    check the input files
# make test     run the tests
# make quick    smoke test (writes results/scratch/, ignored by git)
# make run RUN=fourth_run    full run into results/fourth_run/

PY ?= python3
RUN ?= scratch

.PHONY: setup check test quick run
setup:
	$(PY) -m venv .venv && .venv/bin/pip install -r requirements.txt
check:
	$(PY) -m spar_sim.checks
test: check
	$(PY) -m pytest -q
quick:
	$(PY) -m spar_sim.run --quick
run: test
	$(PY) -m spar_sim.run --out results/$(RUN)
