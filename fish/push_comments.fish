#!/usr/bin/fish

set student_location "/home/jforce/gitolite-admin/bin2018f"
set start (pwd)
set netids
for file_path in ~/Documents/comments/*.tsv
    echo $file_path
    for line in (cat $file_path)
	set parts (string split \t $line)
	echo $parts
	set netid $parts[1]
	echo "netid"
	echo $netid
	echo $netid > netid_list.txt
	set comment $parts[-1]
	echo (string join "/" $student_location "cse3100f18.$netid" "exam1" (string replace ".tsv" ".txt" (string split "/" $file_path)[-1]))
	set location (string join "/" $student_location "cse3100f18.$netid" "exam1" )
	set filename (string replace ".tsv" ".txt" (string split "/" $file_path)[-1])
	cd $location
	
	touch $filename
	echo $comment > $filename
	git add $filename
	set message (string join "" "Comments for " (string replace ".txt" "" $filename))
	echo $message
	git commit -m $message
	git push
	cd 
    end
end

