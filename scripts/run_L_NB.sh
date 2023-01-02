#!/bin/bash

L_I=$(sed -n 3p settings/run_L_NB.yml | tr -d -c 0-9)
DL=$(sed -n 4p settings/run_L_NB.yml | tr -d -c 0-9)
L_F=$(sed -n 5p settings/run_L_NB.yml | tr -d -c 0-9)

for (( L=$L_I ; L<=$L_F ; L=L+$DL ));
do
    python code/config_L_NB.py $L

    N_B_I=$(sed -n 10p settings/run_L_NB.yml | tr -d -c 0-9)
    N_B_F=$(sed -n 11p settings/run_L_NB.yml | tr -d -c 0-9)

    for (( N_B=$N_B_I ; N_B<=$N_B_F ; N_B++ ));
    do
        python code/run_L_NB.py $L $N_B &
    done
done
