#!/bin/bash

python code/config_NB.py

L=$(sed -n 3p settings/run_NB.yml | tr -d -c 0-9)
NI=$(sed -n 8p settings/run_NB.yml | tr -d -c 0-9)
NF=$(sed -n 9p settings/run_NB.yml | tr -d -c 0-9)

for (( nb=$NI ; nb<=$NF ; nb++ ));
do
    python code/run_NB.py $nb &
done
