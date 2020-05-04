#/bin/bash

di=SYSMHC00001
csLoc=ConcatSamples
mgfLoc=mgf
#wget "https://systemhcatlas.org/dataset_replicates/?dataset_id=$di" -O dataset.html --no-check-certificate
#cat dataset.html | grep "<td>\K(SYSMHC.*)(?=</td>)" -oP > sample_list.txt
for i in $(cat sample_list.txt); do
    #wget "https://systemhcatlas.org/dataset_replicates/?dataset_id=$di&sample_id=$i" --no-check-certificate -O "$csLoc/$i.html"
    cat "$csLoc/$i.html" | grep "<td><a href=\"\K(.*\.raw)(?=\">)" -oPi | xargs -n 1 basename | sed -e 's/raw$/mgf/gI' > $csLoc/$i.txt
    if [ $(cat $csLoc/$i.txt | wc -l ) -eq 0 ]; then
       echo "deleting $csLoc/$i.txt"
       #rm $csLoc/$i.txt
    else
	cat $csLoc/$i.txt |  sed -e "s/^/$mgfLoc\//" | xargs awk 1 > $csLoc/$i.mgf
    fi
    
done

