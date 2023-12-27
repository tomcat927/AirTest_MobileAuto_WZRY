cat result.you >> result.you.bak.txt
python3 -u object.py -2 2>&1 | tee result.you

