
.PHONY: test

test:
	@nohup python code/test.py > results/nohup.out &

run:
	@nohup python code/run.py > results/nohup.out &

sequence_NB:
	@python code/sequence_NB.py

run_NB:
	@nohup bash scripts/script_NB.sh > results/nohup.out

clean:
	@rm -rf results/*.out results/*.h5 results/*.log
