#!/usr/bin/env bash
cat result >> result.bak.txt
if [ $1 ]
then
para="$1 1"
else
para=""
fi
python3 -u wzry.py $para  2>&1 | tee result.$1
