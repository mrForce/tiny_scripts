#/bin/bash

di=SYSMHC00001
csLoc=ConcatSamples
mgfLoc=mgf
tsvhLoc=systemhcMatches
mgfFiles=()
tsvhFiles=()
length=0
wget "https://systemhcatlas.org/dataset_replicates/?dataset_id=$di" -O dataset.html --no-check-certificate
cat dataset.html | grep "<td>\K(SYSMHC.*)(?=</td>)" -oP > sample_list.txt
for i in $(cat sample_list.txt); do
    wget "https://systemhcatlas.org/dataset_replicates/?dataset_id=$di&sample_id=$i" --no-check-certificate -O "$csLoc/$i.html"
    cat "$csLoc/$i.html" | grep "<td><a href=\"\K(.*\.raw)(?=\">)" -oPi | xargs -n 1 basename | sed -e 's/raw$/mgf/gI' > $csLoc/$i.txt
    if [ $(cat $csLoc/$i.txt | wc -l ) -eq 0 ]; then
       echo "ignoring $csLoc/$i.txt"
    else
	allMGFFilesExist=true
	mgfsInSample=$( cat $csLoc/$i.txt |  sed -e "s/^/$mgfLoc\//" )
	for x in $mgfsInSample; do
	    if [ ! -f $x ]; then
		allMGFFilesExist=false
	    fi
	done
	if $allMGFFilesExist; then
	    awk 1 $mgfsInSample > $csLoc/$i.mgf
	    wget "https://systemhcatlas.org/mnt/Systemhc/Data/180409_build/$i/Spectrast/cons.tar.gz" -O "$csLoc/$i-cons.tar.gz" --no-check-certificate
	    mkdir $csLoc/$i-cons
	    tar xvf $csLoc/$i-cons.tar.gz -C $csLoc/$i-cons
	    tsvFile=$(find $csLoc/$i-cons -name "consensus.tsvh" | head -n 1)
	    cp $tsvFile $tsvhLoc/$i.tsvh
	    mgfFiles+=("$csLoc/$i.mgf")
	    tsvhFiles+=("$tsvhLoc/$i.tsvh")
	    length=$length+1
	else
	    echo "JORDAN: Not all MGF files in $csLoc/$i.txt exist"
	fi
    fi
done

echo "Pairs"
for (( i=0; i<$length; i++));
do
    echo ${mgfFiles[$i]}"|"${tsvhFiles[$i]}
done



