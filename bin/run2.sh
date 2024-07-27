#!/usr/bin/env bash
cat result.you >> result.you.bak.txt
python3 -u wzry.py -2 2>&1 | tee result.you

