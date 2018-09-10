#!/bin/bash

spreadsheet=$1
spreadsheet_grade_column=$2
huskyct_csv=$3
huskyct_grade_column=$4
echo $#
if [ $# -ne 4 ]; then
    echo "Usage: join_grades.sh grades.csv grade_column huskyct.csv huskyct_grade_column. grades.csv is from Google Drive"
else
    spreadsheet_grades=$(mktemp)
    echo "hi"
    cut -f 1,$spreadsheet_grade_column $spreadsheet | awk '{print $1","$2}'  | sort -t, -k1 > $spreadsheet_grades
    sorted_huskyct=$(mktemp)
    echo "by"
    sort -t, -k3 $huskyct_csv > $sorted_huskyct
    joined=$(mktemp)
    output_string="2.1"
    echo $(seq 1  $[huskyct_grade_column-1])
    num_columns=$(head -n 1 $huskyct_csv | awk '{print NF}')
    for i in $(seq 2 $num_columns );
    do
	if [ $i -eq $huskyct_grade_column ]; then
	    output_string=${output_string}",1.2"
	else
	    output_string=${output_string}",2."$i
	fi
	
    done
   
    echo $spreadsheet_grades
    echo $sorted_huskyct
    echo $output_string
    head -n 1 $huskyct_csv | awk -F "," '{for(i = 1; i < NF; i++){ printf "\"%s\"\t", $i} printf "\"%s\"\n", $NF}'
    join -1 1 -2 3 $spreadsheet_grades $sorted_huskyct -o $output_string -t $',' | awk -F "," '{for(i = 1; i < NF; i++){ printf "\"%s\"\t", $i} printf "\"%s\"\n", $NF}'
fi
