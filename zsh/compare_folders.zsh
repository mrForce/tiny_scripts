#!/usr/bin/zsh

#example: ./compare_folders.zsh ~/cse3100f18.assignments/hw9/hw9 ~/gitolite-admin/list/ids.txt ~/gitolite-admin/bin2018f/cse3100f18.*/hw9 (expand the last one using the tab completion glob thing in ZSH)

function md5SumFolder() {
    #simple trick: just take the folder, md5sum all of the folders, cut out the MD5sums, sort, and re-sum them. 
    md5sum $1/*(.) | cut -c 1-32 | md5sum | cut -c 1-32
}

#$1 is the reference file/folder, $2 is a list of NetIDS, the rest are the folders to check.


if [ -d $1 ];
then
    md5ref=$(md5SumFolder $1)
    for folder in "${@:3}"; do
	tempMD5=$(md5SumFolder $folder)
	if [ "$tempMD5" = "$md5ref" ]; then
	    grep -f $2 <(echo "$folder") -o
	fi
    done
elif [ -f $1 ];
then
    md5ref=$(md5sum $1 | cut -c 1-32)
    for file in "${@:3}"; do
	tempMD5=$(md5sum $file | cut -c 1-32)
	if [ "$tempMD5" = "$md5ref" ]; then
	    grep -f $2 <(echo "$file") -o
	fi
    done
else
    echo "Not a valid file or directory"
fi
