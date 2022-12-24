
test:
	@python code/test.py

run:
	@nohup python code/run.py & > results/nohup.out

sequence_NB:
	@python code/sequence_NB.py

run_NB:
	@nohup bash settings/script_NB.sh > results/nohup.out

clean:
	@rm -rf results/*
	@echo "" >> results/.keep
