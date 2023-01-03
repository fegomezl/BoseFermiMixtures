.PHONY: test run run_NB run_L_NB postproccesing clean

test:
	@nohup python -m tenpy settings/test.yml > results/nohup.out &

run:
	@nohup python code/run.py > results/nohup.out &

run_NB:
	@nohup bash scripts/run_NB.sh > results/nohup.out

run_L_NB:
	@nohup bash scripts/run_L_NB.sh > results/nohup.out

postproccesing:
	@bash scripts/postproccesing.sh

clean:
	@rm -rf results/*.out results/*.h5 results/*.log results/BF*
