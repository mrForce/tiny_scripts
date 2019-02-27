#!/bin/bash
gpg --import secret_key.txt
gpg --output code.zip --decrypt code.zip.gpg
