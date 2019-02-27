#!/bin/bash

gpg --import key.txt
gpg --import-ownertrust otrust.txt
mkdir code
find . -type f | xargs cp -t code
date > code/time.txt
pwd >> code/time.txt
zip -r code.zip code
gpg --output code.zip.gpg --recipient exam.one@example.com --encrypt code.zip
find . -type f ! -name "code.zip.gpg" -delete





