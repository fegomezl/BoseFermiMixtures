.PHONY: test run run_NB run_L_NB clean

test:
	@nohup python -m tenpy settings/test.yml > results/nohup.out &

run:
	@nohup python code/run.py > results/nohup.out &

run_NB:
	@nohup python code/run_NB.py > results/nohup.out &

run_L_NB:
	@nohup python code/run_L_NB.py > results/nohup.out &

clean:
	@rm -rf results/*.out results/*.h5 results/*.log results/BF*

clean_cache:
	@rm -rf code/__pycache__ 	
