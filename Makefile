
test:
	@python code/test.py

run:
	@python code/run.py

sequence_NB:
	@python code/sequence_NB.py

run_NB:
	@nohup bash settings/script_NB.sh > results/nohup.out

clean:
	@rm -rf results/*
	@echo "" >> results/.keep
