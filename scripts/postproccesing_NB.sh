#!/bin/bash

dec_to_sci() {
    local num="$1"
    local prefix="${num%%.*}"

    local sign="+"
    if [[ "$prefix" == "-" ]]; then
        sign="-"
        num=${num#-}
        prefix="${num%%.*}"
    fi

    if [[ "$prefix" == "" ]]; then
        prefix="0"
    fi
    local suffix="${num#*.}"
    if [[ "${suffix}" == "${num}" ]]; then
        suffix="0"
    fi
    if [[ "$prefix" -ne 0 ]]; then
        echo "$sign$prefix.$suffix"
        return 0
    fi
    local without_zeros="${suffix}"
    local num_zeros=0
    while [[ "${without_zeros:0:1}" == "0" ]]; do
        without_zeros="${without_zeros#0}"
        (( num_zeros += 1 ))
    done
    if [[ "$num_zeros" -eq 0 ]]; then
        echo "$sign$prefix.$suffix"
    else
        echo "${sign}0.${without_zeros}e-$(printf "%02d" "$num_zeros")"
    fi
}

#Local analysis
for file in *.log; do
    : > duration_aux.txt
    sed -n '/Current/{s/^[^:]*: \|\s.*//g; p}' "$file" | sed s'/.$//' >> duration_aux.txt

    : > time_aux.txt
    time=0
    while read -r line; do
        time=$(echo "$time" + "$line" | bc)
        echo "$time" >> time_aux.txt
    done < duration_aux.txt

    : > energy_aux.txt
    sed -n '/energy/{s/^[^=]*=\|\,.*//g; p}' "$file" >> energy_aux.txt

    echo "NaN" > E_err_aux.txt
    old_energy=$(head -n 1 energy_aux.txt)
    { read -r;
        while read -r line;do 
            abs_energy=${line#-}
            delta_energy=$(echo "$old_energy" - "$line" | bc)
            E_err=$(echo "scale=16 ; $delta_energy/$abs_energy" | bc)
            E_err=$(dec_to_sci "$E_err")
            echo "$E_err" >> E_err_aux.txt
            old_energy=$line
        done } < energy_aux.txt

    : > S_err_aux.txt
    sed -n '/Delta E/{s/^[^,]*,\|\ (.*//g; p}' "$file" | sed -n "s/^[^=]*= \|\ (.*//g; p" >> S_err_aux.txt

    echo -e "duration\n$(cat duration_aux.txt)" > duration_aux.txt
    echo -e "time\n$(cat time_aux.txt)" > time_aux.txt
    echo -e "energy\n$(cat energy_aux.txt)" > energy_aux.txt
    echo -e "E_err\n$(cat E_err_aux.txt)" > E_err_aux.txt
    echo -e "S_err\n$(cat S_err_aux.txt)" > S_err_aux.txt

    filename=${file%.*}
    filename="${filename}.csv"
    paste time_aux.txt duration_aux.txt energy_aux.txt E_err_aux.txt S_err_aux.txt > "$filename"
    rm time_aux.txt duration_aux.txt energy_aux.txt E_err_aux.txt S_err_aux.txt
done

#Global analysis
: > data_aux.txt
for file in *.csv; do
    nb="$file"
    nb=$file
    nb=${nb%%_NFU*}
    nb=${nb#*NB}
    energy="$(tail -n 1 "$file" | cut -f3)"
    time="$(tail -n 1 "$file" | cut -f1)"
    E_err="$(tail -n 1 "$file" | cut -f4)"
    S_err="$(tail -n 1 "$file" | cut -f5)"
    echo "$nb $energy $time $E_err $S_err" >> data_aux.txt
done

current_dir=${PWD##*/}
output="${current_dir}.txt"
: > "$output"
echo "nb energy time E_err S_err" > "$output"
sort -n data_aux.txt >> "$output"
echo -e "\n============================\n" >> "$output"
rm data_aux.txt

#Append log files
: > order_aux.txt
for file in *.log; do
    name=$file
    name=${name%%_NFU*}
    name=${name#*NB}
    echo "$name $file" >> order_aux.txt
done

sort -n order_aux.txt > order.txt
rm order_aux.txt

while read -r file; do
    file=${file#* }
    cat "$file" >> "$output"
done < order.txt
rm order.txt

rm *.log
