#!/bin/bash

dir="results"
for file in ${dir}/*/
  do
    file="${file%%/}"  
    echo "${file##.*/}"
    cd ${file##.*/}; bash ../../scripts/postproccesing_NB.sh ; cd ..; cd ..
  done
