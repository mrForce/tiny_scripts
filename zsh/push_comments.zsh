#!/usr/bin/zsh

BASES=()
student_location="/home/jforce/gitolite-admin/bin2018f"
start=$(pwd)
for file_path in ~/Documents/comments/*.tsv;		
do
    dos2unix $file_path
    num_points=$(head -n 1 $file_path)
    base=$(basename $file_path .tsv)
    #of the format: comment\t score\t location
    awk_output=$(gawk -v num_points=$num_points -v base=$base -v student_location="$student_location" -F $'\t' 'BEGIN {OFS=FS
    PROCINFO["NONFATAL"] = 1} { 
    PROCFINFO["NONFATAL"] = 1
    ERRNO=0
    print $NF > student_location"/cse3100f18."$1"/exam1/"base".txt"	
    print "score: " $(NF-1) " out of: " num_points > student_location"/cse3100f18."$1"/exam1/"base".txt"
    print student_location"/cse3100f18."$1"/exam1/"base".txt" > "paths.txt" 
    		
    }' <(tail -n +3 $file_path))
    BASES+=($base)
done
for path_thing in $student_location/cse3100f18.*;
do
    cd $path_thing"/exam1"
    for  base in $BASES;
    do
	git add $path_thing"/exam1/"$base".txt"
    done
    git commit -m "Pushing comments and scores"
    git push
done
