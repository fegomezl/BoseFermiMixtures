#!/bin/bash
L=$(sed -n 3p settings/run_NB.yml | tr -d -c 0-9)

python code/config_NB.py

for (( nb=0 ; nb<=$L ; nb++ ));
do
    python code/run_NB.py $nb &
done
