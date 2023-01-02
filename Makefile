.PHONY: test run run_NB clean

test:
	@nohup python -m tenpy settings/test.yml > results/nohup.out &

run:
	@nohup python code/run.py > results/nohup.out &

run_NB:
	@nohup bash scripts/run_NB.sh > results/nohup.out

run_L_NB:
	@nohup bash scripts/run_L_NB.sh > results/nohup.out

clean:
	@rm -rf results/*.out results/*.h5 results/*.log results/BF*
