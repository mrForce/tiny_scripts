#!/bin/bash

LOC=$(ssh cd9 'mktemp -d')
echo $LOC
scp $1 jordan@cd9:$LOC
base="$(basename -- $1)"
ssh cd9 'python3 /home/jordan/flurry_run.py '"$LOC/$base $LOC"'/output '${@:3}
scp jordan@cd9:$LOC/output $2
ssh cd9 'rm -r '"$LOC"
