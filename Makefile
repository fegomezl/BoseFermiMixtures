.PHONY: run run_NB test clean

test:
	@python code/test.py

run:
	@python code/run.py

run_NB:
	@python code/run_NB.py

clean:
	@rm -rf results/*
	@echo "" >> results/.keep
