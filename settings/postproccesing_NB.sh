#!/bin/bash

#Energy
: > energy_aux.txt
for file in *.log; do
    name=$file
    name=${name%%_NFU*}
    name=${name#*NB}
    data=$(sed -n '/energy/{s/^[^=]*=\|\,.*//g; p}' $file | tail -n1)
    echo "$name $data" >> energy_aux.txt
done

#Performance
echo "nb energy" > energy.txt
sort -n energy_aux.txt >> energy.txt
rm energy_aux.txt

for file in *.log; do
    echo 'energy' > energy_aux.txt 
    sed -n '/energy/{s/^[^=]*=\|\,.*//g; p}' $file >> energy_aux.txt

    echo 'duration' > time_aux.txt 
    sed -n '/Current/{s/^[^:]*: \|\s.*//g; p}' $file | sed s'/.$//' >> time_aux.txt

    echo 'entropy_change' > entropy_aux.txt 
    sed -n '/Delta E/{s/^[^,]*,\|\ (.*//g; p}' $file | sed -n "s/^[^=]*= \|\ (.*//g; p" >> entropy_aux.txt

    filename=${file%.*}
    filename="${filename}.txt"
    paste time_aux.txt energy_aux.txt entropy_aux.txt > $filename
    rm time_aux.txt energy_aux.txt entropy_aux.txt
done

#Log files
: > order_aux.txt
for file in *.log; do
    name=$file
    name=${name%%_NFU*}
    name=${name#*NB}
    echo "$name $file" >> order_aux.txt
done

sort -n order_aux.txt > order.txt
rm order_aux.txt

current_dir=${PWD##*/}
output="${current_dir}.txt"
: > $output
while read file; do
    file=${file#* }
    cat $file >> $output
done < order.txt
rm order.txt

rm *.log
