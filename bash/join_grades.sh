#!/bin/bash



spreadsheet=$1
spreadsheet_grade_column=$2
huskyct_csv=$3
huskyct_grade_column=$4

if [ $# -ne 4 ]; then
    echo "Usage: join_grades.sh grades.csv grade_column huskyct.csv huskyct_grade_column. grades.csv is from Google Drive"
    echo "Example of usage: ./join_grades.sh ~/temp/lab0_spreadsheet.csv 12 ~/Downloads/gc_M1188-CSE-3100-001.011_column_2018-09-10-18-01-41.csv 8"
else
    spreadsheet_grades=$(mktemp)
    cut -f 1,$spreadsheet_grade_column $spreadsheet | awk '{print $1","$2}'  | sort -t, -k1 > $spreadsheet_grades
    sorted_huskyct=$(mktemp)
    sort -t, -k3 <(sed 's/\"//g' $huskyct_csv) > $sorted_huskyct
    joined=$(mktemp)
    output_string="2.1"

    num_columns=$(head -n 1 $huskyct_csv | sed 's/\"//g' | awk -F "," '{print NF}')
    for i in $(seq 2 $num_columns );
    do
	if [ $i -eq $huskyct_grade_column ]; then
	    output_string=${output_string}",1.2"
	else
	    output_string=${output_string}",2."$i
	fi
	
    done
   
    head -n 1 $huskyct_csv 
    join -1 1 -2 3 $spreadsheet_grades $sorted_huskyct -o $output_string -t $',' | awk -F "," '{for(i = 1; i < NF; i++){ printf "\"%s\"\t", $i} printf "\"%s\"\n", $NF}'
fi


