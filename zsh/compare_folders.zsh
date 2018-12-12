#!/usr/bin/zsh



function md5SumFolder() {
   #simple trick: just take the folder, md5sum all of the folders, cut out the MD5sums, sort, and re-sum them. 
    md5sum $1/*(.) | cut -c 1-32 | md5sum | cut -c 1-32
}

#$1 is the reference folder, $2 is a list of NetIDS, the rest are the folders to check.
md5ref=$(md5SumFolder $1)

for file in "${@:3}"; do
    tempMD5=$(md5SumFolder $file)
    if [ "$tempMD5" = "$md5ref" ]; then
	grep -f $2 <(echo "$file") -o
    fi
done
