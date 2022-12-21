#!/bin/bash

N=10

echo "Profilling(N=$N)" > results.txt
echo "nproc   mean(T)   stdev(T)" >> results.txt
for i in 1 2 3 4
do
    export MKL_NUM_THREADS=$i
    python BFChain.py $i $N
done
