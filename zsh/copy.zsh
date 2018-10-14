#!/bin/zsh

vm_location="/home/jforce/sshfs/sysProgVM"
lab_folder="lab5"

for file in cse3100f18.*;
do
    echo $file;
    echo "Making: " ${vm_location}/${file}
    mkdir ${vm_location}/${file}
    echo "Copying: " ${file}/${lab_folder}
    cp -r ${file}/${lab_folder} ${vm_location}/${file}
done
